import { useState } from 'react';
import { useModels } from '../hooks/useApi';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

export function Models() {
  const { data: models, isLoading, error } = useModels();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedCapability, setSelectedCapability] = useState('');

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Models</h1>
          <p className="mt-2 text-gray-600">
            Explore and manage LLM providers and model configurations
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Failed to load models. Please try again.</p>
        </div>
      </div>
    );
  }

  // Filter models based on search and filters
  const filteredModels = models?.filter(model => {
    const matchesSearch = !searchTerm || 
      model.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      model.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      model.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesProvider = !selectedProvider || model.provider === selectedProvider;
    const matchesCapability = !selectedCapability || 
      model.capabilities?.includes(selectedCapability);
    
    return matchesSearch && matchesProvider && matchesCapability;
  }) || [];

  // Get unique providers and capabilities for filters
  const providers = models ? [...new Set(models.map(m => m.provider).filter(Boolean))] : [];
  const capabilities = models ? [...new Set(models.flatMap(m => m.capabilities || []))] : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Models</h1>
        <p className="mt-2 text-gray-600">
          Explore and manage LLM providers and model configurations
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search models..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
          
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Providers</option>
            {providers.map(provider => (
              <option key={provider} value={provider}>{provider}</option>
            ))}
          </select>
          
          <select
            value={selectedCapability}
            onChange={(e) => setSelectedCapability(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Capabilities</option>
            {capabilities.map(capability => (
              <option key={capability} value={capability}>{capability}</option>
            ))}
          </select>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {filteredModels.length} model{filteredModels.length !== 1 ? 's' : ''} found
            </span>
            <button
              type="button"
              onClick={() => {
                setSearchTerm('');
                setSelectedProvider('');
                setSelectedCapability('');
              }}
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              Clear filters
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4">
                  <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : filteredModels.length > 0 ? (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="space-y-4">
              {filteredModels.map((model, index) => (
                <div key={model.id || index} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-900">
                          {model.display_name || model.id}
                        </h4>
                        {model.provider && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            {model.provider}
                          </span>
                        )}
                      </div>
                      {model.description && (
                        <p className="text-sm text-gray-500 mt-1">
                          {model.description}
                        </p>
                      )}
                      <div className="mt-2 flex flex-wrap gap-4 text-xs text-gray-500">
                        {model.context_window && (
                          <span>Context: {model.context_window.toLocaleString()} tokens</span>
                        )}
                        {model.input_cost_per_token && (
                          <span>Input: ${(model.input_cost_per_token * 1000000).toFixed(2)}/1M tokens</span>
                        )}
                        {model.output_cost_per_token && (
                          <span>Output: ${(model.output_cost_per_token * 1000000).toFixed(2)}/1M tokens</span>
                        )}
                        {model.multimodal && (
                          <span className="text-green-600">Multimodal</span>
                        )}
                        {model.reasoning && (
                          <span className="text-purple-600">Reasoning</span>
                        )}
                      </div>
                      {model.capabilities && model.capabilities.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {model.capabilities.map((cap: string) => (
                            <span key={cap} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              {cap}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <button
                        type="button"
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Select
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-center py-12">
              <FunnelIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No models found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search criteria or filters.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}