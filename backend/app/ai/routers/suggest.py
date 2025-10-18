from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from backend.app.ai.schemas.chat import Suggestion
from backend.app.api.deps import User, get_current_user

router = APIRouter()


@router.get("/suggest", response_model=List[Suggestion])
async def suggest_endpoint(user: User = Depends(get_current_user)) -> List[Suggestion]:
    base_suggestions = [
        Suggestion(
            title="المقيمون المتأخرون",
            body="تحقق من قائمة المتأخرين لأكثر من 14 يوماً.",
            action="payments.overdue",
        ),
        Suggestion(
            title="الصيانة الوقائية",
            body="راجع جدول صيانة معدات السلامة للأسبوع القادم.",
            action="inventory.schedule_maintenance",
        ),
    ]

    if user.role == "resident":
        return [
            Suggestion(
                title="متابعة الدفعات",
                body="يمكنك السؤال عن الفاتورة الحالية أو سجل دفعاتك.",
            )
        ]

    if user.role == "supervisor":
        base_suggestions.append(
            Suggestion(
                title="إرسال تذكير",
                body="أرسل إشعاراً للمقيمين المتأخرين لتسوية الدفعات.",
                action="notifications.create",
            )
        )

    base_suggestions.append(
        Suggestion(
            title="استخدام المساعد الذكي",
            body="اطلب من المساعد إنشاء تقرير المدفوعات الأسبوعي تلقائياً.",
        )
    )
    return base_suggestions
