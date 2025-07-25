export function Models() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Models</h1>
        <p className="mt-2 text-gray-600">
          Manage LLM providers and model configurations
        </p>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Available Models
          </h3>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">OpenAI GPT-4.1</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Most capable model for complex reasoning tasks
                  </p>
                  <div className="mt-2 flex space-x-4 text-xs text-gray-500">
                    <span>Context: 1M tokens</span>
                    <span>Cost: $5.00/$15.00 per 1M tokens</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Groq Llama 3.3 70B</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    High-speed inference optimized model
                  </p>
                  <div className="mt-2 flex space-x-4 text-xs text-gray-500">
                    <span>Context: 8K tokens</span>
                    <span>Speed: ~280 tokens/sec</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Available
                </span>
              </div>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Claude 3.5 Sonnet</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Balanced performance and intelligence
                  </p>
                  <div className="mt-2 flex space-x-4 text-xs text-gray-500">
                    <span>Context: 200K tokens</span>
                    <span>Quality: High</span>
                  </div>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Available
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}