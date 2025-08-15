import { 
  HomeIcon, 
  CpuChipIcon, 
  Cog6ToothIcon, 
  RectangleGroupIcon, 
  ChartBarIcon, 
  UsersIcon,
  PlusIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

/**
 * Demo component to showcase icon sizing fixes
 * This component demonstrates that icons are properly constrained
 */
export function IconSizingDemo() {
  return (
    <div className="p-8 space-y-8 bg-white">
      <h1 className="text-2xl font-bold text-gray-900">Icon Sizing Demo</h1>
      
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-700">Navigation Icons (w-6 h-6)</h2>
        <nav className="flex space-x-4">
          <HomeIcon className="w-6 h-6 text-blue-500" />
          <CpuChipIcon className="w-6 h-6 text-green-500" />
          <RectangleGroupIcon className="w-6 h-6 text-purple-500" />
          <ChartBarIcon className="w-6 h-6 text-orange-500" />
          <UsersIcon className="w-6 h-6 text-red-500" />
          <Cog6ToothIcon className="w-6 h-6 text-gray-500" />
        </nav>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-700">Button Icons (w-5 h-5)</h2>
        <div className="flex space-x-4">
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="w-5 h-5 mr-2" />
            Add New
          </button>
          <button className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            <PlayIcon className="w-5 h-5 mr-2" />
            Execute
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-700">Small Action Icons (w-4 h-4)</h2>
        <div className="flex space-x-2">
          <button className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <PlayIcon className="w-4 h-4" />
          </button>
          <button className="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Cog6ToothIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-700">Global Constraints Test</h2>
        <p className="text-sm text-gray-600">
          These icons without explicit sizing should be constrained by global CSS (max 2rem):
        </p>
        <div className="flex space-x-4">
          <HomeIcon className="text-blue-500" />
          <CpuChipIcon className="text-green-500" />
          <RectangleGroupIcon className="text-purple-500" />
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-md p-4">
        <p className="text-green-800 text-sm">
          ✅ All icons should be properly sized and not render at full page size.
          The global CSS constraints ensure that even icons without explicit sizing are bounded.
        </p>
      </div>
    </div>
  );
}