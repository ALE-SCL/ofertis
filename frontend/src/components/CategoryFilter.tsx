import React from 'react';
import { LayoutGrid, Beef, Ham, Drumstick, Milk, Wheat, Utensils } from 'lucide-react';
import { CategoryItem } from '../types';

interface CategoryFilterProps {
  categories: CategoryItem[];
  selectedCategory: string;
  onSelectCategory: (slug: string) => void;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  LayoutGrid: <LayoutGrid className="w-4 h-4" />,
  Beef: <Beef className="w-4 h-4" />,
  Ham: <Ham className="w-4 h-4" />,
  Drumstick: <Drumstick className="w-4 h-4" />,
  Milk: <Milk className="w-4 h-4" />,
  Wheat: <Wheat className="w-4 h-4" />,
  Utensils: <Utensils className="w-4 h-4" />
};

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  selectedCategory,
  onSelectCategory
}) => {
  return (
    <div className="flex items-center space-x-2 overflow-x-auto py-2 px-1 custom-scrollbar">
      {categories.map((cat) => {
        const isSelected = selectedCategory === cat.slug;
        const icon = ICON_MAP[cat.icon] || <LayoutGrid className="w-4 h-4" />;

        return (
          <button
            key={cat.slug}
            onClick={() => onSelectCategory(cat.slug)}
            className={`flex items-center space-x-2 whitespace-nowrap px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 shadow-sm ${
              isSelected
                ? 'bg-blue-600 text-white shadow-blue-500/20 shadow-md scale-105'
                : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 hover:border-slate-300'
            }`}
          >
            <span className={isSelected ? 'text-white' : 'text-blue-600'}>{icon}</span>
            <span>{cat.name}</span>
          </button>
        );
      })}
    </div>
  );
};
