import { useCallback, useEffect, useState } from 'react'
import {
  App as AntApp,
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Table,
  Tag,
  Typography,
} from 'antd'
import { PlusOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { api } from '../api/client.js'
import { LABELS } from '../constants/labels.js'
import { useAuth } from '../auth/AuthContext.jsx'
import { CAN_WRITE_STOCK } from '../constants/roles.js'

const { Title, Text } = Typography

export default function ProductsPage() {
  // useApp 必須在元件內呼叫（Hook 只能在 render 階段使用）
  const { message, modal } = AntApp.useApp()
  const { user } = useAuth()
  // 唯讀與銷貨員不可異動品項（FR-30）
  const canWrite = CAN_WRITE_STOCK.includes(user?.role)
  const [data, setData] = useState({ items: [], total: 0, page: 1, page_size: 50 })
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const load = useCallback(async (params = {}) => {
    setLoading(true)
    try {
      const result = await api.listProducts(params)
      setData(result)
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    load({ page: 1, page_size: 50 })
  }, [load])

  const handleSearch = (value) => {
    setKeyword(value)
    load({ keyword: value, page: 1, page_size: 50 })
  }

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const created = await api.createProduct(values)
      message.success(`品項已建立：${created.name}`)
      setOpen(false)
      form.resetFields()
      await load({ keyword, page: 1, page_size: 50 })
    } catch (error) {
      if (error?.errorFields) return // 表單欄位驗證錯誤，由 AntD 顯示
      message.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDeactivate = (record) => {
    modal.confirm({
      title: `確定要停用「${record.name}」嗎？`,
      content: '停用後不會再出現在新建單據的品項清單中，但歷史紀錄仍保留。',
      okText: '停用',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.updateProduct(record.id, { is_active: false })
          message.success(`已停用：${record.name}`)
          await load({ keyword, page: data.page, page_size: data.page_size })
        } catch (error) {
          message.error(error.message)
        }
      },
    })
  }

  const columns = [
    {
      title: LABELS.sku,
      dataIndex: 'sku',
      key: 'sku',
      width: 140,
    },
    {
      title: LABELS.name,
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: LABELS.category,
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (value) => value || '—',
    },
    {
      title: LABELS.unit,
      dataIndex: 'unit',
      key: 'unit',
      width: 90,
    },
    {
      title: LABELS.price,
      dataIndex: 'price',
      key: 'price',
      width: 110,
      className: 'num',
    },
    {
      title: LABELS.safetyQty,
      dataIndex: 'safety_qty',
      key: 'safety_qty',
      width: 110,
      className: 'num',
    },
    {
      title: LABELS.leadTimeDays,
      dataIndex: 'lead_time_days',
      key: 'lead_time_days',
      width: 130,
      className: 'num',
    },
    {
      title: '狀態',
      key: 'status',
      width: 110,
      render: (_, record) =>
        record.is_active ? <Tag color="success">啟用</Tag> : <Tag>已停用</Tag>,
    },
    {
      title: '',
      key: 'actions',
      width: 100,
      render: (_, record) =>
        record.is_active && canWrite ? (
          <Popconfirm
            title="確定要停用這個品項嗎？"
            description="停用後不會再出現在新建單據的品項清單中。"
            okText="停用"
            okButtonProps={{ danger: true }}
            cancelText="取消"
            onConfirm={() => handleDeactivate(record)}
          >
            <Button type="link" danger size="small">
              停用
            </Button>
          </Popconfirm>
        ) : null,
    },
  ]

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 16,
        }}
      >
        <div>
          <Title level={4} style={{ margin: 0 }}>
            {LABELS.products}
          </Title>
          <Text type="secondary">
            建立與管理品項主檔；後續的入庫、出庫、盤點、補貨都以品項為對象。
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setOpen(true)}
          disabled={!canWrite}
          title={canWrite ? undefined : '你的角色不能異動品項'}
        >
          新增品項
        </Button>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Input
          allowClear
          prefix={<SearchOutlined />}
          placeholder="以 sku 或名稱搜尋"
          style={{ maxWidth: 320 }}
          onPressEnter={(e) => handleSearch(e.target.value)}
          onChange={(e) => {
            if (e.target.value === '') handleSearch('')
          }}
        />
        <Button icon={<ReloadOutlined />} onClick={() => load({ keyword, page: 1, page_size: 50 })}>
          重新整理
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data.items}
        pagination={{
          current: data.page,
          pageSize: data.page_size,
          total: data.total,
          showSizeChanger: false,
          onChange: (page) => load({ keyword, page, page_size: data.page_size }),
        }}
        locale={{
          emptyText: (
            <div style={{ padding: 24 }}>
              <div>還沒有品項。先建立一個品項，才能登記入庫。</div>
              {canWrite && (
                <Button type="primary" style={{ marginTop: 12 }} onClick={() => setOpen(true)}>
                  新增品項
                </Button>
              )}
            </div>
          ),
        }}
      />

      <Modal
        title="新增品項"
        open={open}
        onOk={handleCreate}
        onCancel={() => {
          setOpen(false)
          form.resetFields()
        }}
        confirmLoading={saving}
        okText="建立"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="sku"
            label={LABELS.sku}
            rules={[{ required: true, message: 'sku 不能空白' }]}
          >
            <Input placeholder="例：A-001" />
          </Form.Item>
          <Form.Item
            name="name"
            label={LABELS.name}
            rules={[{ required: true, message: '名稱不能空白' }]}
          >
            <Input placeholder="例：可樂 500ml" />
          </Form.Item>
          <Form.Item name="category" label={LABELS.category}>
            <Input placeholder="例：飲料" />
          </Form.Item>
          <Form.Item name="unit" label={LABELS.unit} initialValue="個">
            <Input placeholder="例：瓶" />
          </Form.Item>
          <Form.Item name="price" label={LABELS.price} initialValue={0}>
            <InputNumber min={0} precision={2} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="safety_qty" label={LABELS.safetyQty} initialValue={0}>
            <InputNumber min={0} precision={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="lead_time_days"
            label={`${LABELS.leadTimeDays}（補貨前置天數）`}
            initialValue={7}
            tooltip="這個品項從下單到貨進來要幾天。留空預設 7 天。"
          >
            <InputNumber min={0} precision={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
