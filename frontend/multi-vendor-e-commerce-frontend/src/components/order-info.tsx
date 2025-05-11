import { useNavigate } from 'react-router-dom';
import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getUserOrders } from '@/requests/getOrder';



export function OrderInfo() {

    const location = useLocation();
    const navigate = useNavigate();
    const userInfo = location.state;
    const userEmail = userInfo.userEmail;
    const userToken = userInfo.userToken;

    const [orders, setOrders] = useState<any[]>([]); // State to store fetched orders
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null); // State for handling errors

    const handleReturn = () => {
        navigate('/dashboard', {
            state: { userEmail, userToken },
        });
    };

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const fetchedOrders = await getUserOrders(userEmail);
                setOrders(fetchedOrders); // Assuming the API returns an array of orders
            } catch (err) {
                setError('Failed to fetch orders. Please try again later.');
            } finally {
                setLoading(false);
            }
        };

        fetchOrders();
    }, [userEmail]);

    if (loading) {
        return <div>Loading...</div>; // Optionally show a loading spinner
    }

    if (error) {
        return <div className=' flex mt-100'><div /* logo-div */ onClick={handleReturn} className="w-1/2 flex">
            <img
                src="src/assets/landing-page/shop-svgrepo-com.svg"
                alt="Description of image"
                className="w-10 h-10 ml-60"
            />
            <p className="text-2xl ml-1 mb-1 italic font-bold">Shoply</p>
        </div>{error}</div>; // Display error message
    }



    return (
        <div /* Container */ className="min-h-screen flex-col">
            <div /* Content */ className="h-30 w-1/1 flex">
                <div /* logo-div */ onClick={handleReturn} className="w-1/2 content-center items-center flex">
                    <img
                        src="src/assets/landing-page/shop-svgrepo-com.svg"
                        alt="Description of image"
                        className="w-10 h-10 ml-60"
                    />
                    <p className="text-2xl ml-1 mb-1 italic font-bold">Shoply</p>
                </div>
            </div>

            <div /* Information */ className="flex w-1/1 h-1/2">
                <div className="w-full p-4">
                    <h2 className="text-xl font-semibold mb-4">Your Orders</h2>
                    {orders.length > 0 ? (
                        <div>
                            {orders.map((order, index) => (
                                <div key={index} className="border p-4 mb-2 rounded-md shadow-md">
                                    <h3 className="font-bold">Order #{order.id}</h3>
                                    <p>Status: {order.status}</p>
                                    <p>Date: {new Date(order.date).toLocaleDateString()}</p>
                                    <h4 className="mt-2">Items:</h4>
                                    <ul>
                                        {order.items.map((item: any, idx: number) => (
                                            <li key={idx}>
                                                {item.product_name} - Quantity: {item.quantity} - Unit Price: ${item.unit_price}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p>No orders found.</p>
                    )}
                </div>
            </div>
        </div>
    );
}