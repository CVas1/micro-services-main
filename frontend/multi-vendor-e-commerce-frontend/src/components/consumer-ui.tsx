import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import CategoryMenu from "./category-menu";
import getConsumerAxiosInstance from "@/requests/consumerAxiosInstance";
import { AxiosError } from "axios";
import ProductGrid from './product-grid.tsx';
import {
    DropdownMenu,
    DropdownMenuTrigger,
    DropdownMenuContent,
    DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useCart } from '../hooks/CartContext.tsx';




export function ConsumerUi() {

    const maxProducts = 15;
    const navigate = useNavigate();
    const [searched, setSearched] = useState("");
    const [categories, setCategories] = useState<{ Id: string; Name: string; ParentId: string }[]>([]);
    const [products, setProducts] = useState<{
        Id: string;
        Name: string;
        Description: string;
        Price: number;
        Stock: number;
        CategoryId: string;
        Image: string;
        VendorId: string;
    }[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

    const { cart } = useCart();

    const location = useLocation();
    const userEmail = location.state.userEmail;
    const userToken = location.state.userToken;

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearched(e.target.value);
    };


    const handleProfileClick = () => {
        navigate('/profile', {
            state: { userEmail, userToken },
        });
    };

    const handleReturn = () => {
        navigate('/');
    };

    const handleOrderClick = () => {
        navigate('/order', {
            state: { userEmail, userToken },
        });
    };

    const handleOrderInfo = () => {
        navigate('/order-info', {
            state: { userEmail, userToken },
        });
    };

    const handleSearchButtonClick = () => {
        if (searched.trim() !== "") {
            searchProductsByName(searched.trim());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            handleSearchButtonClick();
        }
    };

    const searchProductsByName = async (name: string) => {
        const axios = await getConsumerAxiosInstance();
        try {
            const response = await axios?.get(`/product/many/${name}`, {
                params: { name: name }
            });
            if (response?.status === 200) {
                setProducts(response.data.data);  // Update the product list with search results
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                console.error("Product search error:", problemDetails.detail);
            } else {
                console.error("An unexpected error occurred while searching products.");
            }
        }
    };

    // Fetch Categories
    async function getCategories(): Promise<{ Id: string; Name: string; ParentId: string }[] | null> {
        const axios = await getConsumerAxiosInstance();
        try {
            const response = await axios?.get('/category');
            if (response?.status === 200) {
                return response.data.data; // Assuming response.data.data is an array of category objects
            }
            return null;
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                console.error("Category fetch error:", problemDetails.detail);
            } else {
                console.error("An unexpected error occurred while fetching categories.");
            }
            return null;
        }
    }

    // Fetch products based on category
    const fetchProductsByCategory = async (categoryId: string) => {
        const axios = await getConsumerAxiosInstance();
        try {
            const response = await axios?.get(`/product/category/${categoryId}`);
            if (response?.status === 200) {
                setProducts(response.data.data);  // Set the products fetched for the selected category
            }
        } catch (error: unknown) {
            if (error instanceof AxiosError) {
                console.error("Product fetch error:", error.message);
            }
        }
    };

    // Fetch all products (if no category is selected)
    async function getProducts(): Promise<{
        Id: string;
        Name: string;
        Description: string;
        Price: number;
        Stock: number;
        CategoryId: string;
        Image: string;
        VendorId: string;
    }[] | null> {
        const axios = await getConsumerAxiosInstance();
        try {
            const response = await axios?.get('/product');
            if (response?.status === 200) {
                return response.data.data; // Assuming response.data.data is an array of product objects
            }
            return null;
        } catch (error: unknown) {
            if (error instanceof AxiosError && error.response) {
                const problemDetails: { detail: string } = error.response.data;
                console.error("Product fetch error:", problemDetails.detail);
            } else {
                console.error("An unexpected error occurred while fetching products.");
            }
            return null;
        }
    }

    // Fetch categories on component mount
    useEffect(() => {
        const fetchCategories = async () => {
            const data = await getCategories();
            if (data) setCategories(data); // Set categories correctly
            console.log(data); // Log to check the fetched data
        };
        fetchCategories();
    }, []);

    // Fetch products when category is selected or when no category is selected (to fetch all products)
    useEffect(() => {
        if (selectedCategory) {
            fetchProductsByCategory(selectedCategory);
        } else {
            const fetchAllProducts = async () => {
                const data = await getProducts();
                if (data) setProducts(data); // Set products correctly
                console.log(data); // Log to check the fetched data
            };
            fetchAllProducts();
        }
    }, [selectedCategory]);

    const handleCategorySelect = (categoryId: string) => {
        setSelectedCategory(categoryId);  // Update the selected category
    };

    return (
        <div /* Container */ className="min-h-screen flex-col ">
            <div /* Content */ className="h-33 w-1/1 flex ">
                <div /* logo-div */ className="w-1/3 items-center flex">
                    <button
                        onClick={() => window.location.reload()} // Reload the page on click
                        className="flex items-center"
                    >
                        <img
                            src="src\assets\landing-page\shop-svgrepo-com.svg"
                            alt="Description of image"
                            className="w-10 h-10 ml-60"
                        />
                        <p className="text-2xl ml-1 mb-1 italic font-bold">Shoply</p>
                    </button>
                </div>
                <div /* search-bar */ className="w-1/3 items-center flex">
                    <Input
                        type="text"
                        placeholder="Search"
                        value={searched}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        className="w-150 h-12 placeholder:text-base placeholder:font-200 border-2 border-gray-300 rounded-3xl"
                    />
                    <Button className=" bg-translucent absolute flex transform mt-10 ml-137 -translate-y-1/2 h-10 px-1 text-sm rounded-3xl ">
                        <img
                            src="src\assets\search-alt-2-svgrepo-com.svg"
                            alt="Description of image"
                            className="w-10 h-10"
                            onClick={handleSearchButtonClick}
                        />
                    </Button>
                </div>
                <div /* Button-div */ className="w-1/3 items-center flex">
                    <Button onClick={handleOrderClick} className=" ml-60 relative h-10 p-2 shadow-none bg-transparent hover:bg-gray-100">
                        <img
                            src="src/assets/bag-shopping-svgrepo-com.svg"
                            alt="Cart"
                            className="w-8 h-8"
                        />
                        {cart.length > 0 && (
                            <span className="absolute top-0 right-0 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center transform translate-x-1/2 -translate-y-1/2">
                                {cart.length}
                            </span>
                        )}
                    </Button>
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <img
                                src="src\assets\user.svg"
                                alt="Clickable"
                                className="w-10 ml-10 h-10 cursor-pointer rounded-lg hover:shadow-lg transition-shadow duration-200"
                            />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuItem onClick={handleProfileClick}>Profile</DropdownMenuItem>
                            <DropdownMenuItem onClick={handleOrderInfo}>Orders</DropdownMenuItem>
                            <DropdownMenuItem onClick={handleReturn}>Signout</DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
            <div className="h-200 w-1/1 flex">
                <div /* Category-menu div */ className="flex h-1/1 w-55 ml-60">
                    <CategoryMenu categories={categories} onCategorySelect={handleCategorySelect} />
                </div>
                <div /* Products-menu div */ className="flex h-3/4 w-1.05/2">
                    {products.length > 0 ? (
                        <ProductGrid products={products} maxProducts={maxProducts} />
                    ) : (
                        <p>No products found for the selected category.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
