import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

/**
 * {{toolDisplayName}}
 *
 * {{description}}
 */
export const {{toolName}}Tool = createTool({
  id: '{{toolId}}',
  description: '{{description}}',
  inputSchema: z.object({{inputSchema}}),
  outputSchema: z.object({{outputSchema}}),
  execute: async ({ inputData }) => {
    {{executeBody}}
  },
});

export default {{toolName}}Tool;
