import getOrchestrationAxiosInstance from './orchestrationAxiosInstance';

interface OrderItem {
  product_id: string;
  quantity: number;
  unit_price: number;
}

interface OrderPayload {
  user_email: string;
  vendor_email: string;
  delivery_address: string;
  description: string;
  status: 'Pending' | string;
  items: OrderItem[];
  payment_method: string;
}

export async function startOrder(order: OrderPayload) {
  try {
    const axiosInstance = await getOrchestrationAxiosInstance(); // ✅ Await here
    if (!axiosInstance) throw new Error('Failed to get axios instance');

    const response = await axiosInstance.post('/order/create_order', order);
    return response.data;
  } catch (error) {
    console.error('Order creation failed:', error);
    throw error;
  }
}
