import { Layout, Menu, Typography, Tag, Dropdown, Button } from 'antd'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { DownOutlined, LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { AuthProvider, useAuth } from './auth/AuthContext.jsx'
import LoginPage from './pages/LoginPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'
import StockInPage from './pages/StockInPage.jsx'
import UsersPage from './pages/UsersPage.jsx'
import { ROLE } from './constants/roles.js'

const { Sider, Content, Header } = Layout
const { Title, Text } = Typography

function Shell() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
        <Text type="secondary">載入中…</Text>
      </div>
    )
  }

  if (!user) return <LoginPage />

  const isAdmin = user.role === ROLE.ADMIN

  const menu = [
    {
      key: 'catalog',
      label: '設定',
      children: [
        { key: 'products', label: <Link to="/products">品項</Link> },
        ...(isAdmin
          ? [{ key: 'users', label: <Link to="/users">使用者管理</Link> }]
          : []),
      ],
    },
    {
      key: 'daily',
      label: '日常作業',
      children: [
        { key: 'stock-in', label: <Link to="/stock-in">入庫</Link> },
        { key: 'stock-out', label: '出庫', disabled: true },
        { key: 'stocktake', label: '盤點', disabled: true },
      ],
    },
    {
      key: 'query',
      label: '查詢',
      children: [
        { key: 'stock', label: '庫存查詢', disabled: true },
        { key: 'movements', label: '異動紀錄', disabled: true },
      ],
    },
    {
      key: 'analysis',
      label: '分析',
      children: [
        { key: 'reports', label: '報表', disabled: true },
        { key: 'replenishment', label: '補貨判斷', disabled: true },
        { key: 'performance', label: '銷貨員業績', disabled: true },
      ],
    },
  ]

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px 20px 8px' }}>
          <Title level={5} style={{ margin: 0, color: '#1F6F5C' }}>
            庫存管理系統
          </Title>
        </div>
        <Menu mode="inline" defaultSelectedKeys={['products']} items={menu} />
      </Sider>
      <Layout>
        <Header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingInline: 24,
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            品項主檔
          </Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Tag color="processing">MVP 開發中 · Story 1.2 ～ 1.9</Tag>
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'info',
                    label: (
                      <span>
                        {user.display_name}（{user.username}）· {user.role_label}
                      </span>
                    ),
                    disabled: true,
                  },
                  { type: 'divider' },
                  { key: 'logout', label: '登出', icon: <LogoutOutlined />, onClick: handleLogout },
                ],
              }}
            >
              <Button icon={<UserOutlined />}>
                {user.display_name} · {user.role_label} <DownOutlined />
              </Button>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ padding: 24 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/products" replace />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/stock-in" element={<StockInPage />} />
            <Route
              path="/users"
              element={isAdmin ? <UsersPage /> : <Navigate to="/products" replace />}
            />
            <Route
              path="*"
              element={
                <div style={{ color: '#8c8c8c' }}>
                  這個畫面還沒做出來（Story 尚未實作）。先到「品項」頁試用。
                </div>
              }
            />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}
