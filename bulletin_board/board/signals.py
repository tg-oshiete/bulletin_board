from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .models import Response, Ad
import logging
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User


logger = logging.getLogger(__name__) #


@receiver(post_save, sender=Response)
def send_response_email(sender, instance, created, **kwargs):
    if created:
        try:
            ad = instance.ad
            author = ad.author
            responder = instance.from_user
            subject = f'Новый отклик на ваше объявление "{ad.title}"'
            html_message = render_to_string('board/emails/new_response.html', {
                'ad': ad,
                'response': instance,
                'author': author,
                'responder': responder,
                'site_name': 'MMORPG Форум'
            })
            plain_message = f"""
            Здравствуйте, {author.username}!

            Пользователь {responder.username} оставил отклик на ваше объявление "{ad.title}".

            Текст отклика:
            {instance.text}

            Вы можете просмотреть и принять отклик в личном кабинете:
            {settings.SITE_URL}/bulletin-board/responses/

            С уважением,
            Команда MMORPG Форума
            """
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email отправлен автору {author.email} о новом отклике на объявление {ad.id}")

        except Exception as e:
            logger.error(f"Ошибка отправки email о новом отклике: {e}")


@receiver(post_save, sender=Response)
def send_response_accepted_email(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_response = Response.objects.get(pk=instance.pk)
            if not old_response.is_accepted and instance.is_accepted:
                ad = instance.ad
                responder = instance.from_user
                author = ad.author
                subject = f'Ваш отклик на объявление "{ad.title}" принят!'
                html_message = render_to_string('board/emails/response_accepted.html', {
                    'ad': ad,
                    'response': instance,
                    'responder': responder,
                    'author': author,
                    'site_name': 'MMORPG Форум'
                })
                plain_message = f"""
                Поздравляем, {responder.username}!

                Автор {author.username} принял ваш отклик на объявление "{ad.title}".

                Теперь вы можете связаться с автором для дальнейшего обсуждения:
                Email автора: {author.email}

                Текст вашего отклика:
                {instance.text}

                С уважением,
                Команда MMORPG Форума
                """
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[responder.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Email отправлен {responder.email} о принятии отклика на объявление {ad.id}")

        except Response.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Ошибка отправки email о принятии отклика: {e}")


@receiver(post_save, sender=Ad)
def send_ad_created_email(sender, instance, created, **kwargs):
    if created:
        try:
            author = instance.author
            subject = f'Ваше объявление "{instance.title}" успешно создано!'
            html_message = render_to_string('board/emails/ad_created.html', {
                'ad': instance,
                'author': author,
                'site_name': 'MMORPG Форум'
            })

            plain_message = f"""
            Здравствуйте, {author.username}!

            Ваше объявление "{instance.title}" успешно создано и опубликовано на MMORPG Форуме.

            Категория: {instance.category.name}
            Дата создания: {instance.created.strftime('%d.%m.%Y %H:%M')}

            Вы можете просмотреть своё объявление по ссылке:
            {settings.SITE_URL}/bulletin-board/{instance.pk}/

            Управлять откликами можно в личном кабинете:
            {settings.SITE_URL}/bulletin-board/responses/

            С уважением,
            Команда MMORPG Форума
            """

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Email отправлен автору {author.email} о создании объявления {instance.id}")

        except Exception as e:
            logger.error(f"Ошибка отправки email о создании объявления: {e}")


def send_newsletter_to_all_users(subject, message, html_message=None):
    try:
        users = User.objects.filter(is_active=True, profile__email_notifications=True)
        email_list = [(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                      for user in users]
        send_mass_mail(email_list, fail_silently=False)
        logger.info(f"Рассылка отправлена {len(email_list)} пользователям")
        return len(email_list)

    except Exception as e:
        logger.error(f"Ошибка отправки рассылки: {e}")
        return 0