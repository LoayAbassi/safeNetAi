def get_otp_email_template(language='en'):
    """Get OTP email template based on language"""
    templates = {
        'en': {
            'subject': 'SafeNetAi - Email Verification OTP',
            'title': 'Email Verification',
            'greeting': 'Hello {user_name}!',
            'message': 'Welcome to SafeNetAi! Please use the verification code below to complete your email verification and activate your account.',
            'code_label': 'Your Verification Code',
            'expires_in': 'This code expires in {hours} hours',
            'instructions_title': 'How to verify your email:',
            'instructions': [
                'Copy the 6-digit code above',
                'Return to the SafeNetAi verification page',
                'Enter the code in the verification field',
                'Click "Verify" to complete the process'
            ],
            'security_notice': 'Security Notice: If you didn\'t request this verification, please ignore this email. Your account security is our top priority.',
            'support': 'Need help? Contact our support team at support@safenetai.com',
            'footer': 'Advanced AI-Powered Financial Security',
            'copyright': '© 2025 SafeNetAi. All rights reserved.'
        },
        'fr': {
            'subject': 'SafeNetAi - Code de vérification OTP',
            'title': 'Vérification d\'email',
            'greeting': 'Bonjour {user_name}!',
            'message': 'Bienvenue sur SafeNetAi ! Veuillez utiliser le code de vérification ci-dessous pour terminer la vérification de votre email et activer votre compte.',
            'code_label': 'Votre code de vérification',
            'expires_in': 'Ce code expire dans {hours} heures',
            'instructions_title': 'Comment vérifier votre email :',
            'instructions': [
                'Copiez le code à 6 chiffres ci-dessus',
                'Retournez à la page de vérification de SafeNetAi',
                'Entrez le code dans le champ de vérification',
                'Cliquez sur "Vérifier" pour terminer le processus'
            ],
            'security_notice': 'Avis de sécurité : Si vous n\'avez pas demandé cette vérification, veuillez ignorer cet email. La sécurité de votre compte est notre priorité absolue.',
            'support': 'Besoin d\'aide ? Contactez notre équipe de support à support@safenetai.com',
            'footer': 'Sécurité financière alimentée par l\'IA',
            'copyright': '© 2025 SafeNetAi. Tous droits réservés.'
        },
        'ar': {
            'subject': 'SafeNetAi - رمز التحقق عبر البريد الإلكتروني',
            'title': 'التحقق من البريد الإلكتروني',
            'greeting': 'مرحباً {user_name}!',
            'message': 'مرحباً بك في SafeNetAi! يرجى استخدام رمز التحقق أدناه لإكمال التحقق من بريدك الإلكتروني وتفعيل حسابك.',
            'code_label': 'رمز التحقق الخاص بك',
            'expires_in': 'هذا الرمز ينتهي في غضون {hours} ساعات',
            'instructions_title': 'كيفية التحقق من بريدك الإلكتروني:',
            'instructions': [
                'انسخ الرمز المكون من 6 أرقام أعلاه',
                'عد إلى صفحة التحقق من SafeNetAi',
                'أدخل الرمز في حقل التحقق',
                'انقر على "تحقق" لإكمال العملية'
            ],
            'security_notice': 'إشعار أمني: إذا لم تطلب هذا التحقق، يرجى تجاهل هذا البريد الإلكتروني. أمان حسابك هو أولويتنا القصوى.',
            'support': 'هل تحتاج إلى مساعدة؟ اتصل بفريق الدعم لدينا على support@safenetai.com',
            'footer': 'الأمان المالي المدعوم بالذكاء الاصطناعي',
            'copyright': '© 2025 SafeNetAi. جميع الحقوق محفوظة.'
        }
    }
    
    return templates.get(language, templates['en'])

def get_security_otp_email_template(language='en'):
    """Get security OTP email template based on language"""
    templates = {
        'en': {
            'subject': '🔒 Security Verification Required - Transaction #{transaction_id}',
            'title': 'Security Verification Required',
            'alert_title': '⚠️ Unusual Activity Detected',
            'alert_message': 'We\'ve detected unusual activity and need to verify this transaction.',
            'greeting': 'Hello <strong>{user_name}</strong>,',
            'message': 'Our AI-powered security system has flagged a transaction on your account that requires additional verification before processing.',
            'transaction_details': '💳 Transaction Details',
            'transaction_id': 'Transaction ID:',
            'amount': 'Amount:',
            'type': 'Type:',
            'risk_score': 'Risk Score:',
            'status': 'Status:',
            'code_label': 'Your Security Code',
            'expires_in': 'This code expires in 10 minutes',
            'instructions_title': 'Complete your transaction:',
            'instructions': [
                'Copy the 6-digit security code above',
                'Return to your SafeNetAi transaction page',
                'Enter the code when prompted',
                'Click "Verify" to complete your transaction'
            ],
            'security_warning': 'Security Notice: If you didn\'t initiate this transaction, please contact our security team immediately at security@safenetai.com or call +213-XXX-XXXX.',
            'dashboard_button': 'Access Your Dashboard',
            'support': 'Need assistance? Our security team is available 24/7 to help protect your account.',
            'footer': 'Advanced AI-Powered Financial Protection',
            'copyright': '© 2025 SafeNetAi Security Team',
            'auto_message': 'This security alert was automatically generated. Please do not reply to this email.'
        },
        'fr': {
            'subject': '🔒 Vérification de sécurité requise - Transaction #{transaction_id}',
            'title': 'Vérification de sécurité requise',
            'alert_title': '⚠️ Activité inhabituelle détectée',
            'alert_message': 'Nous avons détecté une activité inhabituelle et devons vérifier cette transaction.',
            'greeting': 'Bonjour <strong>{user_name}</strong>,',
            'message': 'Notre système de sécurité alimenté par l\'IA a signalé une transaction sur votre compte qui nécessite une vérification supplémentaire avant traitement.',
            'transaction_details': '💳 Détails de la transaction',
            'transaction_id': 'ID de transaction:',
            'amount': 'Montant:',
            'type': 'Type:',
            'risk_score': 'Score de risque:',
            'status': 'Statut:',
            'code_label': 'Votre code de sécurité',
            'expires_in': 'Ce code expire dans 10 minutes',
            'instructions_title': 'Terminez votre transaction:',
            'instructions': [
                'Copiez le code de sécurité à 6 chiffres ci-dessus',
                'Retournez à la page de transaction de SafeNetAi',
                'Entrez le code lorsque vous y êtes invité',
                'Cliquez sur "Vérifier" pour terminer votre transaction'
            ],
            'security_warning': 'Avis de sécurité : Si vous n\'avez pas initié cette transaction, veuillez contacter immédiatement notre équipe de sécurité à security@safenetai.com ou appelez le +213-XXX-XXXX.',
            'dashboard_button': 'Accéder à votre tableau de bord',
            'support': 'Besoin d\'aide ? Notre équipe de sécurité est disponible 24/7 pour protéger votre compte.',
            'footer': 'Protection financière alimentée par l\'IA',
            'copyright': '© 2025 Équipe de sécurité de SafeNetAi',
            'auto_message': 'Cette alerte de sécurité a été générée automatiquement. Veuillez ne pas répondre à cet email.'
        },
        'ar': {
            'subject': '🔒 مطلوب التحقق الأمني - المعاملة #{transaction_id}',
            'title': 'مطلوب التحقق الأمني',
            'alert_title': '⚠️ تم اكتشاف نشاط غير عادي',
            'alert_message': 'لقد اكتشفنا نشاطًا غير عادي ونحتاج إلى التحقق من هذه المعاملة.',
            'greeting': 'مرحباً <strong>{user_name}</strong>,',
            'message': 'لقد قام نظام الأمان المدعوم بالذكاء الاصطناعي لدينا بوضع علامة على معاملة في حسابك تتطلب التحقق الإضافي قبل المعالجة.',
            'transaction_details': '💳 تفاصيل المعاملة',
            'transaction_id': 'رقم المعاملة:',
            'amount': 'المبلغ:',
            'type': 'النوع:',
            'risk_score': 'درجة المخاطرة:',
            'status': 'الحالة:',
            'code_label': 'رمز الأمان الخاص بك',
            'expires_in': 'هذا الرمز ينتهي في غضون 10 دقائق',
            'instructions_title': 'أكمل معاملتك:',
            'instructions': [
                'انسخ رمز الأمان المكون من 6 أرقام أعلاه',
                'عد إلى صفحة معاملات SafeNetAi',
                'أدخل الرمز عند الطلب',
                'انقر على "تحقق" لإكمال معاملتك'
            ],
            'security_warning': 'إشعار أمني: إذا لم تقم ببدء هذه المعاملة، يرجى الاتصال بفريق الأمان لدينا فورًا على security@safenetai.com أو الاتصال بالرقم +213-XXX-XXXX.',
            'dashboard_button': 'الوصول إلى لوحة التحكم الخاصة بك',
            'support': 'هل تحتاج إلى مساعدة؟ فريق الأمان لدينا متاح على مدار الساعة طوال أيام الأسبوع لحماية حسابك.',
            'footer': 'الحماية المالية المدعومة بالذكاء الاصطناعي',
            'copyright': '© 2025 فريق أمان SafeNetAi',
            'auto_message': 'تم إنشاء تنبيه الأمان هذا تلقائيًا. يرجى عدم الرد على هذا البريد الإلكتروني.'
        }
    }
    
    return templates.get(language, templates['en'])

def get_transaction_notification_template(language='en'):
    """Get transaction notification email template based on language"""
    templates = {
        'en': {
            'subject': 'SafeNetAi - Transaction {status}',
            'title': 'Transaction Notification',
            'greeting': 'Hello {user_name},',
            'message': 'Your transaction has been <strong>{status}</strong> successfully.',
            'transaction_details': 'Transaction Details',
            'transaction_id': 'Transaction ID:',
            'amount': 'Amount:',
            'type': 'Type:',
            'status_label': 'Status:',
            'date': 'Date:',
            'risk_level': 'Risk Level:',
            'risk_score': 'Risk Score:',
            'dashboard_button': 'View Dashboard',
            'footer_message': 'If you have any questions, please contact our support team.',
            'footer': 'Advanced AI-Powered Financial Security',
            'copyright': '© 2025 SafeNetAi. All rights reserved.',
            'auto_message': 'This is an automated message, please do not reply.'
        },
        'fr': {
            'subject': 'SafeNetAi - Transaction {status}',
            'title': 'Notification de transaction',
            'greeting': 'Bonjour {user_name},',
            'message': 'Votre transaction a été <strong>{status}</strong> avec succès.',
            'transaction_details': 'Détails de la transaction',
            'transaction_id': 'ID de transaction:',
            'amount': 'Montant:',
            'type': 'Type:',
            'status_label': 'Statut:',
            'date': 'Date:',
            'risk_level': 'Niveau de risque:',
            'risk_score': 'Score de risque:',
            'dashboard_button': 'Voir le tableau de bord',
            'footer_message': 'Si vous avez des questions, veuillez contacter notre équipe de support.',
            'footer': 'Sécurité financière alimentée par l\'IA',
            'copyright': '© 2025 SafeNetAi. Tous droits réservés.',
            'auto_message': 'Ceci est un message automatisé, veuillez ne pas répondre.'
        },
        'ar': {
            'subject': 'SafeNetAi - المعاملة {status}',
            'title': 'إشعار المعاملة',
            'greeting': 'مرحباً {user_name},',
            'message': 'لقد تم <strong>{status}</strong> معاملتك بنجاح.',
            'transaction_details': 'تفاصيل المعاملة',
            'transaction_id': 'رقم المعاملة:',
            'amount': 'المبلغ:',
            'type': 'النوع:',
            'status_label': 'الحالة:',
            'date': 'التاريخ:',
            'risk_level': 'مستوى المخاطرة:',
            'risk_score': 'درجة المخاطرة:',
            'dashboard_button': 'عرض لوحة التحكم',
            'footer_message': 'إذا كانت لديك أي أسئلة، يرجى الاتصال بفريق الدعم لدينا.',
            'footer': 'الأمان المالي المدعوم بالذكاء الاصطناعي',
            'copyright': '© 2025 SafeNetAi. جميع الحقوق محفوظة.',
            'auto_message': 'هذا رسالة تلقائية، يرجى عدم الرد.'
        }
    }
    
    return templates.get(language, templates['en'])

def get_fraud_alert_template(language='en'):
    """Get fraud alert email template based on language"""
    templates = {
        'en': {
            'subject': 'SafeNetAi - Security Alert - Unusual Activity Detected',
            'title': 'Security Alert',
            'alert_banner': '⚠️ Security Alert',
            'alert_message': 'We detected unusual activity on your account that requires your attention.',
            'greeting': 'Hello {user_name},',
            'message': 'Our AI-powered security system has flagged a transaction on your account as potentially suspicious.',
            'transaction_details': 'Transaction Details',
            'transaction_id': 'Transaction ID:',
            'amount': 'Amount:',
            'type': 'Type:',
            'risk_level': 'Risk Level:',
            'risk_score': 'Risk Score:',
            'triggers': 'Triggers:',
            'review_button': 'Review Transaction',
            'warning_message': 'If you don\'t recognize this transaction, please contact our security team immediately.',
            'footer': 'Advanced AI-Powered Financial Protection',
            'copyright': '© 2025 SafeNetAi. All rights reserved.',
            'auto_message': 'This is an automated security alert, please do not reply.'
        },
        'fr': {
            'subject': 'SafeNetAi - Alerte de sécurité - Activité inhabituelle détectée',
            'title': 'Alerte de sécurité',
            'alert_banner': '⚠️ Alerte de sécurité',
            'alert_message': 'Nous avons détecté une activité inhabituelle sur votre compte qui nécessite votre attention.',
            'greeting': 'Bonjour {user_name},',
            'message': 'Notre système de sécurité alimenté par l\'IA a signalé une transaction sur votre compte comme potentiellement suspecte.',
            'transaction_details': 'Détails de la transaction',
            'transaction_id': 'ID de transaction:',
            'amount': 'Montant:',
            'type': 'Type:',
            'risk_level': 'Niveau de risque:',
            'risk_score': 'Score de risque:',
            'triggers': 'Déclencheurs:',
            'review_button': 'Examiner la transaction',
            'warning_message': 'Si vous ne reconnaissez pas cette transaction, veuillez contacter immédiatement notre équipe de sécurité.',
            'footer': 'Protection financière alimentée par l\'IA',
            'copyright': '© 2025 SafeNetAi. Tous droits réservés.',
            'auto_message': 'Ceci est une alerte de sécurité automatisée, veuillez ne pas répondre.'
        },
        'ar': {
            'subject': 'SafeNetAi - تنبيه أمني - تم اكتشاف نشاط غير عادي',
            'title': 'تنبيه أمني',
            'alert_banner': '⚠️ تنبيه أمني',
            'alert_message': 'لقد اكتشفنا نشاطًا غير عادي في حسابك يتطلب انتباهك.',
            'greeting': 'مرحباً {user_name},',
            'message': 'لقد قام نظام الأمان المدعوم بالذكاء الاصطناعي لدينا بوضع علامة على معاملة في حسابك كمشبوهة محتملة.',
            'transaction_details': 'تفاصيل المعاملة',
            'transaction_id': 'رقم المعاملة:',
            'amount': 'المبلغ:',
            'type': 'النوع:',
            'risk_level': 'مستوى المخاطرة:',
            'risk_score': 'درجة المخاطرة:',
            'triggers': 'المؤثرات:',
            'review_button': 'مراجعة المعاملة',
            'warning_message': 'إذا لم تكن تعرف هذه المعاملة، يرجى الاتصال بفريق الأمان لدينا فورًا.',
            'footer': 'الحماية المالية المدعومة بالذكاء الاصطناعي',
            'copyright': '© 2025 SafeNetAi. جميع الحقوق محفوظة.',
            'auto_message': 'هذا تنبيه أمني تلقائي، يرجى عدم الرد.'
        }
    }
    
    return templates.get(language, templates['en'])