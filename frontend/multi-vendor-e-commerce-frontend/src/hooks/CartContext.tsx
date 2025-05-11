import React, { createContext, useContext, useEffect, useState } from 'react';
import { CartItem } from '../types';

const LOCAL_STORAGE_KEY = 'cartItems';

interface CartContextType {
  cart: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  removeAllOfItem: (id: string) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<CartItem[] | null>(null); // Use null for loading state

  // Load from localStorage only once
  useEffect(() => {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (stored) {
      setCart(JSON.parse(stored));
    } else {
      setCart([]); // Initialize empty cart if nothing stored
    }
  }, []);

  // Save to localStorage when cart is available and changes
  useEffect(() => {
    if (cart !== null) {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(cart));
    }
  }, [cart]);

  const addItem = (item: CartItem) => {
    if (cart === null) return;
    setCart(prev => [...(prev ?? []), item]);
  };

  const removeAllOfItem = (id: string) => {
    if (cart === null) return;
    const newCart = cart.filter(item => item.id !== id);
    setCart(newCart);
  };

  const removeItem = (id: string) => {
    if (cart === null) return;
    const index = cart.findIndex(i => i.id === id);
    if (index !== -1) {
      const newCart = [...cart];
      newCart.splice(index, 1);
      setCart(newCart);
    }
  };

  const clearCart = () => setCart([]);

  // Don't render children until cart is loaded
  if (cart === null) return null;

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem, removeAllOfItem , clearCart }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};


