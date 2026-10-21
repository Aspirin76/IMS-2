import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App as AntApp, ConfigProvider } from 'antd'
import zhTW from 'antd/locale/zh_TW'
import App from './App.jsx'

// DESIGN.md：主色墨綠、強調橘（僅用於需立即行動的情況）
const theme = {
  token: {
    colorPrimary: '#1F6F5C',
    colorError: '#C2410C',
    borderRadius: 8,
    fontFamily:
      '"Segoe UI", "Microsoft JhengHei", "PingFang TC", system-ui, sans-serif',
  },
  components: {
    Layout: { siderBg: '#FFFFFF', headerBg: '#FFFFFF' },
  },
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ConfigProvider locale={zhTW} theme={theme}>
      <AntApp>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  </React.StrictMode>,
)
