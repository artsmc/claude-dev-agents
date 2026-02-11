import { Agent } from '@mastra/core';

/**
 * {{agentDisplayName}}
 *
 * {{description}}
 */
export const {{agentName}}Agent = new Agent({
  id: '{{agentId}}',
  name: '{{agentDisplayName}}',
  instructions: `{{instructions}}`,
  model: {
    provider: '{{provider}}',
    model: '{{model}}',
  },
  tools: [{{tools}}], // Array of tool IDs
});

export default {{agentName}}Agent;
