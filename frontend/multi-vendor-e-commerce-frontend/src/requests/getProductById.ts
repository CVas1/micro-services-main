import { AxiosError } from 'axios';
import getConsumerAxiosInstance from "@/requests/consumerAxiosInstance";

interface Product {
  Id: string;
  Name: string;
  Description: string;
  Price: number;
  Stock: number;
  VendorId: string;
  Image: string;
  CategoryId: string;
}

export async function getProductById(id: string): Promise<Product | null> {
  const axios = await getConsumerAxiosInstance();
  try {
    const response = await axios?.get(`/product/${id}`);
    if (response?.status === 200) {
      return response.data.data;
    }
    return null;
  } catch (error: unknown) {
    if (error instanceof AxiosError && error.response) {
      console.error("Product fetch error:", error.response.data?.detail);
    } else {
      console.error("An unexpected error occurred while fetching the product.");
    }
    return null;
  }
}
