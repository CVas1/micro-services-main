import { AxiosError } from 'axios';
import getOrderAxiosInstance from './orderAxiosInstance';  // Import your instance

export const getUserOrders = async (email: string) => {
    try {
        // Fetching the orders using your existing Axios instance
        const instance = await getOrderAxiosInstance();
        if (!instance) {
            throw new Error('Failed to initialize the Axios instance');
        }

        const response = await instance.get(`/orders/user/${email}`);
        return response.data; // Assuming response contains the orders
    } catch (error: unknown) {  // Explicitly set the error type to 'unknown'
        if (error instanceof AxiosError) {
            // Handle AxiosError-specific properties
            console.error("Error fetching orders:", error.message);
        } else if (error instanceof Error) {
            // Handle generic JavaScript errors
            console.error("General error:", error.message);
        } else {
            // Handle other unknown error types
            console.error("An unknown error occurred");
        }
        throw error;  // Rethrow error to handle it in the component
    }
};
