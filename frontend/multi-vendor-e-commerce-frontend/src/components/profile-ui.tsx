import { useNavigate } from 'react-router-dom';
import { useLocation } from "react-router-dom";
import { AxiosError } from 'axios';
import getAuthAxiosInstance from "@/requests/authAxiosInstance";
import { useEffect, useState } from "react";



export function ProfileUi() {

    const location = useLocation();
    const navigate = useNavigate();
    const userInfo = location.state;
    const [user, setUser] = useState<any>(null);

    const userEmail = userInfo.userEmail;
    const userToken = userInfo.userToken;

    async function findUserByEmail(email: string): Promise<any | null> {
        const axios = await getAuthAxiosInstance();

        try {
            const response = await axios?.get(`/user/${encodeURIComponent(email)}`);
            if (response?.status === 200) {
                console.log('User found:', response.data);
                return response.data;
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                console.error('User lookup error:', problemDetails.detail);
            } else {
                console.error('An unexpected error occurred during user lookup.');
            }
        }

        return null;
    }

    useEffect(() => {
        const fetchUser = async () => {
            if (userInfo.userEmail) {
                const userData = await findUserByEmail(userInfo.userEmail);
                setUser(userData);
            }
        };

        fetchUser();
    }, []);

    const handleReturn = () => {
        navigate('/dashboard', {
            state: { userEmail, userToken },
        });
    };


    return (
        <div /* Container */ className="min-h-screen flex-col ">
            <div /* Content */ className="h-30 w-1/1 flex ">
                <div /* logo-div */ onClick={handleReturn} className="w-1/2 content-center items-center flex">
                    <img
                        src="src\assets\landing-page\shop-svgrepo-com.svg"
                        alt="Description of image"
                        className="w-10 h-10 ml-60"
                    />
                    <p className="text-2xl ml-1 mb-1 italic font-bold">Shoply</p>
                </div>
            </div>
            <div /* Information */ className=" flex w-1/1 h-1/2">
                {user && (
                    <div className="ml-60 mt-20 w-100 p-4 border rounded-lg shadow-md bg-white space-y-4">
                        <div>
                            <h2 className="text-sm font-semibold text-gray-500">Address</h2>
                            <p className="text-base text-gray-800">{user.address}</p>
                        </div>

                        <div>
                            <h2 className="text-sm font-semibold text-gray-500">Full Name</h2>
                            <p className="text-base text-gray-800">{user.fullName}</p>
                        </div>

                        <div>
                            <h2 className="text-sm font-semibold text-gray-500">Phone Number</h2>
                            <p className="text-base text-gray-800">{user.phoneNumber}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}