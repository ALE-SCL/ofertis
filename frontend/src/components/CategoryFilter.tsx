import { 
  LayoutGrid, 
  Beef, 
  Ham, 
  Drumstick, 
  Milk, 
  Wheat, 
  Utensils, 
  ShoppingBag, 
  Coffee, 
  Layers, 
  Sparkles, 
  Heart, 
  Flame, 
  Tag 
} from 'lucide-react';
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
  Utensils: <Utensils className="w-4 h-4" />,
  ShoppingBag: <ShoppingBag className="w-4 h-4" />,
  Coffee: <Coffee className="w-4 h-4" />,
  Layers: <Layers className="w-4 h-4" />,
  Sparkles: <Sparkles className="w-4 h-4" />,
  Heart: <Heart className="w-4 h-4" />,
  Flame: <Flame className="w-4 h-4" />,
  Tag: <Tag className="w-4 h-4" />
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
            className={`flex items-center space-x-2 whitespace-nowrap px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 shadow-xs ${
              isSelected
                ? 'bg-orange-600 text-white shadow-orange-500/25 shadow-md scale-105'
                : 'bg-white dark:bg-stone-900 hover:bg-orange-50/70 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-200 border border-stone-200 dark:border-stone-800 hover:border-orange-200 dark:hover:border-stone-700'
            }`}
          >
            <span className={isSelected ? 'text-white' : 'text-orange-600 dark:text-orange-500'}>{icon}</span>
            <span>{cat.name}</span>
            {cat.count !== undefined && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                isSelected ? 'bg-orange-700 text-orange-100' : 'bg-stone-100 dark:bg-stone-800 text-stone-500 dark:text-stone-400'
              }`}>
                {cat.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
