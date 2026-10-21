import { useState } from 'react'
import { App as AntApp, Button, Card, Form, Input, Typography } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { useAuth } from '../auth/AuthContext.jsx'

const { Title, Text, Paragraph } = Typography

export default function LoginPage() {
  const { login } = useAuth()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const { message } = AntApp.useApp()

  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      await login(values.username, values.password)
      message.success(`歡迎回來，${values.username}`)
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f5f7f6',
        padding: 16,
      }}
    >
      <Card style={{ width: 380, boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>
        <Title level={4} style={{ marginTop: 0, color: '#1F6F5C' }}>
          庫存管理系統
        </Title>
        <Paragraph type="secondary" style={{ marginTop: -4 }}>
          請用帳號登入。登入後，你的操作會記在帳號上，盤點與業績都算得準。
        </Paragraph>

        <Form form={form} layout="vertical" onFinish={handleSubmit} requiredMark={false}>
          <Form.Item name="username" label="帳號" rules={[{ required: true, message: '請輸入帳號' }]}>
            <Input prefix={<UserOutlined />} placeholder="例：admin" autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="密碼" rules={[{ required: true, message: '請輸入密碼' }]}>
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="至少 8 碼"
              autoComplete="current-password"
            />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            登入
          </Button>
        </Form>

        <div style={{ marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            沒有帳號？請管理員在「使用者管理」建立，或用 <code>flask create-admin</code>{' '}
            建立第一位管理員。
          </Text>
        </div>
      </Card>
    </div>
  )
}
