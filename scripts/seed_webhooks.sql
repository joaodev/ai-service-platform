INSERT INTO webhook_configs (event_type, target_url, active)
VALUES
  ('TICKET_CREATED', 'https://n8n.your-domain.com/webhook/ai-platform-events', true),
  ('TRANSACTION_CREATED', 'https://n8n.your-domain.com/webhook/ai-platform-events', true),
  ('WORK_ORDER_STARTED', 'https://n8n.your-domain.com/webhook/ai-platform-events', true)
ON CONFLICT DO NOTHING;
