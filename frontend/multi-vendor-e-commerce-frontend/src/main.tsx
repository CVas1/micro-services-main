import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { BrowserRouter, Route, Routes } from 'react-router';
import App from '@/App.tsx';
import SignInPage from '@/pages/sign-in.tsx';
import SignUpPage from '@/pages/sign-up.tsx';
import LandingPage from './pages/landing';
import ConsumerPage from './pages/consumer';
import ProfilePage from './pages/profile';
import OrderPage from './pages/order';
import OrderInfoPage from './pages/order-info';

// Import the CartProvider
import { CartProvider } from './hooks/CartContext'; // adjust path if needed
import Auth0ProviderWithNavigate from './auth/auth-provider-navigate';
import PrivateRoute from './components/private-route';


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CartProvider>
      <BrowserRouter>
        <Auth0ProviderWithNavigate>
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/landing" element={<LandingPage />} />
            <Route path="/sign-up" element={<SignUpPage />} />
            <Route path="/sign-in" element={<SignInPage />} />
            <Route path="/dashboard" element={<PrivateRoute component={ConsumerPage} role="Customer" />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/order" element={<OrderPage />} />
            <Route path="/order-info" element={<OrderInfoPage />} />
          </Routes>
        </Auth0ProviderWithNavigate>
      </BrowserRouter>
    </CartProvider>
  </StrictMode>,
);
