import { createStep } from '@mastra/core/workflows';
import { z } from 'zod';

/**
 * {{stepDisplayName}}
 *
 * {{description}}
 */
export const {{stepName}}Step = createStep({
  id: '{{stepId}}',
  inputSchema: z.object({{inputSchema}}),
  outputSchema: z.object({{outputSchema}}),
  execute: async ({ inputData }) => {
    {{executeBody}}
  },
});

export default {{stepName}}Step;
