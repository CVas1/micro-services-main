import React from 'react';
import ProductCard from './product-menu';

interface Product {
  Id: string;
  Name: string;
  Price: number;
  Image: string;
}

interface ProductGridProps {
  products: Product[];
  maxProducts: number;  // New prop to limit number of products
}

const ProductGrid: React.FC<ProductGridProps> = ({ products, maxProducts }) => {
  const limitedProducts = products.slice(0, maxProducts);  // Limit the number of products

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-7 p-4 mt-5">
      {limitedProducts.map((product) => (
        <ProductCard key={product.Id} product={product} />
      ))}
    </div>
  );
};

export default ProductGrid;
