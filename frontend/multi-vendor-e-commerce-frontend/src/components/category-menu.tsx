import React from 'react';

// Define the structure of the category object
interface Category {
  Id: string;
  Name: string;
  ParentId: string;
}

interface CategoryMenuProps {
  categories: Category[];  // Array of categories
  onCategorySelect: (categoryId: string) => void;  // Function to handle category selection
}

const CategoryMenu: React.FC<CategoryMenuProps> = ({ categories, onCategorySelect }) => {
  return (
    <div className="w-52 h-screen pt-5 border:transparentshadow-md">
      {categories.map((category) => (
        <a
          key={category.Id}  // Use category Id as the key for better performance
          href="#"
          className="block px-4 py-3 text-gray-800 hover:bg-gray-300 transition-colors duration-200"
          onClick={(e) => {
            e.preventDefault();  // Prevent default anchor behavior
            onCategorySelect(category.Id);  // Trigger the category selection
          }}
        >
          <p className="font-semibold underline dark:text-white">{category.Name}</p>  {/* Render the category name */}
        </a>
      ))}
    </div>
  );
};

export default CategoryMenu;
