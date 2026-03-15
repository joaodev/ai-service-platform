from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models import role, user
from app.models import customer, supplier, product, service
from app.models import ticket, work_order, wallet, transaction
from app.models import accounts_payable, accounts_receivable
from app.models import event_log, webhook_config
from app.models import knowledge_document
from app.models import ai_agent_log
from app.models import background_task
from app.models import ai_agent_action
