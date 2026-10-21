import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  App as AntApp,
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Popconfirm,
  Select,
  Table,
  Tag,
  Typography,
} from 'antd'
import { DeleteOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { api } from '../api/client.js'
import { useAuth } from '../auth/AuthContext.jsx'
import { CAN_WRITE_STOCK } from '../constants/roles.js'

const { Title, Text } = Typography

const emptyRow = () => ({ key: `row-${Math.random().toString(36).slice(2)}`, product_id: null, qty: null, unit_price: null, note: '' })

export default function StockInPage() {
  // useApp 必須在元件內呼叫（Hook 只能在 render 階段使用）
  const { message } = AntApp.useApp()
  const { user } = useAuth()
  const canWrite = CAN_WRITE_STOCK.includes(user?.role)
  const [products, setProducts] = useState([])
  const [rows, setRows] = useState([emptyRow()])
  const [docNo, setDocNo] = useState('')
  const [docDate, setDocDate] = useState(dayjs())
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)
  const [history, setHistory] = useState({ items: [], total: 0 })
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [keyword, setKeyword] = useState('')
  const productRefs = useRef([])

  const loadProducts = useCallback(async () => {
    try {
      const result = await api.listProducts({ page: 1, page_size: 100 })
      setProducts(result.items.filter((p) => p.is_active))
    } catch (error) {
      message.error(error.message)
    }
  }, [message])

  const loadHistory = useCallback(async (kw = '') => {
    setLoadingHistory(true)
    try {
      const result = await api.listDocuments({ type: 'IN', keyword: kw, page: 1, page_size: 20 })
      setHistory(result)
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoadingHistory(false)
    }
  }, [message])

  useEffect(() => {
    loadProducts()
    loadHistory('')
  }, [loadProducts, loadHistory])

  const productOptions = useMemo(
    () =>
      products.map((p) => ({
        value: p.id,
        label: `${p.sku}｜${p.name}`,
        // 顯示目前庫存，讓登記者知道這批進來會變成多少
        title: `目前庫存現量 ${p.safety_qty}（安全庫存）`,
      })),
    [products],
  )

  const totals = useMemo(() => {
    const qty = rows.reduce((sum, r) => sum + (Number(r.qty) || 0), 0)
    const amount = rows.reduce((sum, r) => sum + (Number(r.qty) || 0) * (Number(r.unit_price) || 0), 0)
    return { qty, amount: amount.toFixed(2) }
  }, [rows])

  const updateRow = (key, patch) => {
    setRows((prev) => prev.map((r) => (r.key === key ? { ...r, ...patch } : r)))
  }

  const addRow = () => {
    const row = emptyRow()
    setRows((prev) => [...prev, row])
    // 聚焦到新列的品項欄（連續登錄路徑，UX-DR4）
    setTimeout(() => {
      const index = rows.length
      const ref = productRefs.current[index]
      ref?.focus?.()
    }, 30)
  }

  const removeRow = (key) => {
    setRows((prev) => (prev.length === 1 ? [emptyRow()] : prev.filter((r) => r.key !== key)))
  }

  const handleSubmit = async () => {
    const items = rows
      .filter((r) => r.product_id)
      .map((r) => ({
        product_id: r.product_id,
        qty: r.qty,
        unit_price: r.unit_price,
        note: r.note,
      }))
    if (items.length === 0) {
      message.error('請至少選擇一個品項')
      return
    }
    if (items.some((i) => !i.qty || i.qty <= 0)) {
      message.error('每一列都要有數量')
      return
    }

    setSaving(true)
    try {
      const result = await api.createStockIn({
        doc_no: docNo.trim() || undefined,
        doc_date: docDate.format('YYYY-MM-DD'),
        note: note.trim() || undefined,
        items,
      })
      const summary = result.changes.map((c) => `${c.name}，庫存 ${c.before} → ${c.after}`).join('；')
      message.success(`入庫成功：${summary}`, 5)
      // 表單清空但停留在原頁，記錄者與日期保留，方便連續登錄（UX-DR4）
      setRows([emptyRow()])
      setDocNo('')
      setNote('')
      await Promise.all([loadProducts(), loadHistory(keyword)])
    } catch (error) {
      message.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      title: '品項',
      key: 'product',
      render: (_, row, index) => (
        <Select
          ref={(el) => {
            productRefs.current[index] = el
          }}
          showSearch
          optionFilterProp="label"
          placeholder="搜尋 sku 或名稱"
          style={{ width: '100%' }}
          options={productOptions}
          value={row.product_id}
          onChange={(value) => {
            const product = products.find((p) => p.id === value)
            updateRow(row.key, {
              product_id: value,
              unit_price: row.unit_price ?? (product ? Number(product.price) : null),
            })
          }}
          onPressEnter={() => {
            const current = rows[index]
            if (!current.qty) return
            addRow()
          }}
        />
      ),
    },
    {
      title: '數量',
      key: 'qty',
      width: 140,
      render: (_, row) => (
        <InputNumber
          min={1}
          precision={0}
          style={{ width: '100%' }}
          value={row.qty}
          onChange={(value) => updateRow(row.key, { qty: value })}
          onPressEnter={() => addRow()}
        />
      ),
    },
    {
      title: '單價',
      key: 'unit_price',
      width: 140,
      render: (_, row) => (
        <InputNumber
          min={0}
          precision={2}
          style={{ width: '100%' }}
          value={row.unit_price}
          onChange={(value) => updateRow(row.key, { unit_price: value })}
        />
      ),
    },
    {
      title: '備註',
      key: 'note',
      width: 220,
      render: (_, row) => (
        <Input
          value={row.note}
          placeholder="例：供應商 A 到貨"
          onChange={(e) => updateRow(row.key, { note: e.target.value })}
        />
      ),
    },
    {
      title: '',
      key: 'action',
      width: 60,
      render: (_, row) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeRow(row.key)}
          aria-label="刪除這一列"
        />
      ),
    },
  ]

  const historyColumns = [
    { title: '單號', dataIndex: 'doc_no', key: 'doc_no', width: 190 },
    { title: '日期', dataIndex: 'doc_date', key: 'doc_date', width: 120 },
    { title: '件數', dataIndex: 'total_qty', key: 'total_qty', width: 90, className: 'num' },
    { title: '金額', dataIndex: 'total_amount', key: 'total_amount', width: 120, className: 'num' },
    { title: '記錄者', dataIndex: 'recorded_by', key: 'recorded_by', width: 120 },
    {
      title: '明細',
      key: 'items',
      render: (_, record) =>
        record.items
          .map((i) => `${i.product_id} × ${i.qty}`)
          .join('、') || '—',
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
            入庫
          </Title>
          <Text type="secondary">
            收貨當下登記，庫存現量立刻就對。記錄者會自動帶入你的登入帳號。
          </Text>
        </div>
        {!canWrite && <Tag color="warning">你的角色不能入庫</Tag>}
      </div>

      <Card title="入庫單" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
          <Input
            style={{ width: 220 }}
            placeholder="單號（留空自動產生）"
            value={docNo}
            onChange={(e) => setDocNo(e.target.value)}
            disabled={!canWrite}
          />
          <DatePicker value={docDate} onChange={setDocDate} disabled={!canWrite} />
          <Input
            style={{ width: 320 }}
            placeholder="備註（例：供應商 A 到貨）"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            disabled={!canWrite}
          />
        </div>

        <Table
          rowKey="key"
          columns={columns}
          dataSource={rows}
          pagination={false}
          size="small"
          footer={() => (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Button icon={<PlusOutlined />} onClick={addRow} disabled={!canWrite}>
                新增一列
              </Button>
              <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
                <Text>
                  共 {rows.filter((r) => r.product_id).length} 個品項、{totals.qty} 件
                </Text>
                <Text strong>合計 {totals.amount}</Text>
                <Popconfirm
                  title="確定要送出這張入庫單嗎？"
                  description="送出後庫存現量會立刻更新，且單據不可修改。"
                  okText="送出入庫單"
                  cancelText="取消"
                  onConfirm={handleSubmit}
                >
                  <Button type="primary" loading={saving} disabled={!canWrite}>
                    送出入庫單
                  </Button>
                </Popconfirm>
              </div>
            </div>
          )}
        />
      </Card>

      <Card title="入庫歷史">
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="以單號搜尋"
            style={{ maxWidth: 260 }}
            value={keyword}
            onPressEnter={(e) => loadHistory(e.target.value)}
            onChange={(e) => {
              setKeyword(e.target.value)
              if (e.target.value === '') loadHistory('')
            }}
          />
          <Button onClick={() => loadHistory(keyword)}>搜尋</Button>
        </div>
        <Table
          rowKey="id"
          size="small"
          loading={loadingHistory}
          columns={historyColumns}
          dataSource={history.items}
          pagination={false}
          locale={{ emptyText: '還沒有入庫紀錄。' }}
        />
      </Card>
    </div>
  )
}
