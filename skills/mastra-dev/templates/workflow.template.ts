import { createWorkflow, createStep } from '@mastra/core/workflows';
import { z } from 'zod';

/**
 * {{workflowDisplayName}}
 *
 * {{description}}
 */

// Input/Output schemas
const inputSchema = z.object({{inputSchema}});

const outputSchema = z.object({{outputSchema}});

// Steps
{{steps}}

// Compose workflow from steps
export const {{workflowName}}Workflow = createWorkflow({
  id: '{{workflowId}}',
  description: '{{description}}',
  inputSchema,
  outputSchema,
})
{{composition}}
  .commit();

export default {{workflowName}}Workflow;
