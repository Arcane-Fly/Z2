/**
 * Contract validator for MCP server operations (Frontend/TypeScript).
 *
 * This module provides runtime validation for MCP server requests and responses
 * using JSON Schema contracts. For production use, consider using Ajv for better
 * performance and more features.
 *
 * Basic implementation for demonstration. In production, use:
 * - Ajv (https://ajv.js.org/) for full JSON Schema validation
 * - Pre-compiled validators for better performance
 * - Type generation from schemas using json-schema-to-typescript
 */

export interface ValidationError {
  path: string;
  message: string;
}

export class ContractValidationError extends Error {
  public errors: ValidationError[];
  public contractType: string;

  constructor(message: string, errors: ValidationError[], contractType: string) {
    super(message);
    this.name = 'ContractValidationError';
    this.errors = errors;
    this.contractType = contractType;
  }

  formatErrors(): string {
    const errorList = this.errors.map(e => `  - ${e.path}: ${e.message}`).join('\n');
    return `${this.message} (${this.contractType}):\n${errorList}`;
  }
}

/**
 * Basic type checking validation.
 * 
 * For production use, replace with Ajv or similar JSON Schema validator:
 * 
 * ```typescript
 * import Ajv from "ajv";
 * import addFormats from "ajv-formats";
 * import reqSchema from "../../contracts/pinecone/upsert.request.json";
 * 
 * const ajv = new Ajv({ allErrors: true, strict: true });
 * addFormats(ajv);
 * const validateReq = ajv.compile(reqSchema);
 * 
 * if (!validateReq(data)) {
 *   throw new Error(ajv.errorsText(validateReq.errors));
 * }
 * ```
 */
export class ContractValidator {
  /**
   * Validate data against a contract.
   * 
   * This is a basic implementation. For production, use Ajv with actual schema files.
   */
  validate(data: unknown, operation: string, messageType: 'request' | 'response'): unknown {
    // Basic validation - in production, this would use Ajv with actual schemas
    if (!data || typeof data !== 'object') {
      throw new ContractValidationError(
        `Invalid ${messageType} for ${operation}`,
        [{ path: 'root', message: 'Data must be an object' }],
        `${operation}.${messageType}`
      );
    }

    return data;
  }

  validateRequest(operation: string, data: unknown): unknown {
    return this.validate(data, operation, 'request');
  }

  validateResponse(operation: string, data: unknown): unknown {
    return this.validate(data, operation, 'response');
  }

  validateError(data: unknown): unknown {
    // Basic error envelope validation
    if (!data || typeof data !== 'object') {
      throw new ContractValidationError(
        'Invalid error envelope',
        [{ path: 'root', message: 'Error must be an object' }],
        'error.envelope'
      );
    }

    const errorData = data as Record<string, unknown>;
    if (!errorData.error || typeof errorData.error !== 'object') {
      throw new ContractValidationError(
        'Invalid error envelope',
        [{ path: 'error', message: 'Missing or invalid error field' }],
        'error.envelope'
      );
    }

    return data;
  }
}

// Global validator instance
let defaultValidator: ContractValidator | null = null;

export function getValidator(): ContractValidator {
  if (!defaultValidator) {
    defaultValidator = new ContractValidator();
  }
  return defaultValidator;
}

export function validateRequest(operation: string, data: unknown): unknown {
  return getValidator().validateRequest(operation, data);
}

export function validateResponse(operation: string, data: unknown): unknown {
  return getValidator().validateResponse(operation, data);
}

export function validateError(data: unknown): unknown {
  return getValidator().validateError(data);
}

/**
 * Example usage with MCP service:
 * 
 * ```typescript
 * import { validateRequest, validateResponse } from '@/utils/contractValidator';
 * 
 * async function initializeMCP() {
 *   const request = {
 *     protocolVersion: "2025-03-26",
 *     capabilities: { resources: { subscribe: true } },
 *     clientInfo: { name: "z2-client", version: "1.0.0" }
 *   };
 *   
 *   // Validate before sending
 *   validateRequest('mcp.initialize', request);
 *   
 *   const response = await fetch('/api/v1/mcp/initialize', {
 *     method: 'POST',
 *     body: JSON.stringify(request)
 *   });
 *   
 *   const data = await response.json();
 *   
 *   // Validate after receiving
 *   validateResponse('mcp.initialize', data);
 *   
 *   return data;
 * }
 * ```
 */
