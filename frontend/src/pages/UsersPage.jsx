import { useCallback, useEffect, useState } from 'react'
import { App as AntApp, Button, Form, Input, Modal, Popconfirm, Select, Table, Tag, Typography } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { api } from '../api/client.js'
import { ROLE, ROLE_COLOR, ROLE_LABEL } from '../constants/roles.js'

const { Title, Text } = Typography

export default function UsersPage() {
  // useApp 必須在元件內呼叫（Hook 只能在 render 階段使用）
  const { message, modal } = AntApp.useApp()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.listUsers()
      setUsers(result.items)
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    load()
  }, [load])

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const created = await api.createUser(values)
      message.success(`帳號已建立：${created.display_name}（${created.username}）`)
      setOpen(false)
      form.resetFields()
      await load()
    } catch (error) {
      if (error?.errorFields) return
      message.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDeactivate = (record) => {
    modal.confirm({
      title: `確定要停用「${record.display_name}」嗎？`,
      content: '停用後此帳號無法再登入，但他的歷史紀錄與業績仍會保留。',
      okText: '停用',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.updateUser(record.id, { is_active: false })
          message.success(`已停用：${record.display_name}`)
          await load()
        } catch (error) {
          message.error(error.message)
        }
      },
    })
  }

  const handleResetPassword = (record) => {
    let newPassword = ''
    modal.confirm({
      title: `重設「${record.display_name}」的密碼`,
      content: (
        <Input.Password
          placeholder="輸入新密碼（至少 8 碼）"
          onChange={(e) => {
            newPassword = e.target.value
          }}
        />
      ),
      okText: '重設',
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.updateUser(record.id, { password: newPassword })
          message.success(`已重設 ${record.display_name} 的密碼`)
        } catch (error) {
          message.error(error.message)
          throw error
        }
      },
    })
  }

  const columns = [
    { title: '帳號', dataIndex: 'username', key: 'username', width: 140 },
    { title: '姓名', dataIndex: 'display_name', key: 'display_name', width: 140 },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role) => <Tag color={ROLE_COLOR[role]}>{ROLE_LABEL[role] ?? role}</Tag>,
    },
    {
      title: '狀態',
      key: 'status',
      width: 110,
      render: (_, record) =>
        record.is_active ? <Tag color="success">啟用</Tag> : <Tag>已停用</Tag>,
    },
    {
      title: '最後登入',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      width: 180,
      render: (value) =>
        value ? new Date(value).toLocaleString('zh-TW', { hour12: false }) : '—',
    },
    {
      title: '',
      key: 'actions',
      width: 190,
      render: (_, record) => (
        <>
          <Button type="link" size="small" onClick={() => handleResetPassword(record)}>
            重設密碼
          </Button>
          {record.is_active && (
            <Popconfirm
              title="確定要停用這個帳號嗎？"
              okText="停用"
              okButtonProps={{ danger: true }}
              cancelText="取消"
              onConfirm={() => handleDeactivate(record)}
            >
              <Button type="link" size="small" danger>
                停用
              </Button>
            </Popconfirm>
          )}
        </>
      ),
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
            使用者管理
          </Title>
          <Text type="secondary">
            只有管理員可以建立與停用帳號。銷貨員也是帳號，出貨時會自動記到本人名下。
          </Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>
          新增帳號
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={users}
        pagination={false}
      />

      <Modal
        title="新增帳號"
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
        <Form form={form} layout="vertical" style={{ marginTop: 16 }} initialValues={{ role: ROLE.CLERK }}>
          <Form.Item name="username" label="帳號" rules={[{ required: true, message: '帳號不能空白' }]}>
            <Input placeholder="例：sale03" autoComplete="off" />
          </Form.Item>
          <Form.Item
            name="display_name"
            label="姓名"
            rules={[{ required: true, message: '姓名不能空白' }]}
          >
            <Input placeholder="例：小華" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密碼"
            rules={[
              { required: true, message: '密碼不能空白' },
              { min: 8, message: '密碼至少 8 碼' },
            ]}
          >
            <Input.Password placeholder="至少 8 碼" autoComplete="new-password" />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select
              options={[
                { value: ROLE.ADMIN, label: '管理員（全部功能）' },
                { value: ROLE.CLERK, label: '倉管（入庫、出庫、盤點、品項）' },
                { value: ROLE.SALESPERSON, label: '銷貨員（開出庫單、看自己業績）' },
                { value: ROLE.VIEWER, label: '唯讀（只能看）' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
