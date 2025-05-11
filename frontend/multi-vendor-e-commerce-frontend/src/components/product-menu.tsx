import React from 'react';
import { useCart } from '../hooks/CartContext'; // adjust path if needed
import { CartItem } from '../types'; // adjust path if needed

// Define the structure of the product object
interface Product {
  Id: string;
  Name: string;
  Price: number;
  Image: string;
}

interface ProductCardProps {
  product: Product;  // Product passed as a prop
}


const ProductCard: React.FC<ProductCardProps> = ({ product }) => {

  const { addItem } = useCart();

  const handleAddToCart = () => {
    const item: CartItem = {
      id: product.Id,
      name: product.Name,
      parentId: '', // Set this appropriately if you have a real parent ID
    };
    addItem(item);
    console.log("added");
  };

  return (
    <div className="flex flex-col border rounded-md shadow-md p-1 w-50 h-62  dark:border-3 ">
      <img
        src={product.Image}
        alt={product.Name}
        className="w-full h-35 object-cover rounded-md mb-3 "
      />
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white max-w-xs truncate">{product.Name}</h3>
      <p className="text-gray-600 dark:text-white">${product.Price}</p>
      <button
        onClick={handleAddToCart}
        className="mt-2 px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
      >
        Add to Cart
      </button>
    </div>
  );
};

export default ProductCard;
