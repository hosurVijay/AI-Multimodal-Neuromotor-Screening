package com.neurologicaldisorder.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username}")
    private String fromEmail;

    @Value("${app.frontend.url}")
    private String frontendUrl;

    public void sendPasswordResetEmail(String email, String token) {

        String resetLink = frontendUrl + "/reset-password?token=" + token;

        String htmlBody = """
                <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;
                            padding:32px;border:1px solid #e2e8f0;border-radius:12px;">
                  <h2 style="color:#1e293b;margin-bottom:8px;">Reset your password</h2>
                  <p style="color:#475569;margin-bottom:24px;">
                    We received a request to reset the password for your account.
                    Click the button below to choose a new password.
                    This link expires in <strong>15 minutes</strong>.
                  </p>
                  <a href="%s"
                     style="display:inline-block;background:#6366f1;color:#ffffff;
                            text-decoration:none;padding:12px 28px;border-radius:8px;
                            font-weight:600;font-size:15px;">
                    Reset Password
                  </a>
                  <p style="color:#94a3b8;font-size:13px;margin-top:24px;">
                    If the button doesn't work, copy and paste this link into your browser:<br/>
                    <a href="%s" style="color:#6366f1;word-break:break-all;">%s</a>
                  </p>
                  <p style="color:#cbd5e1;font-size:12px;margin-top:16px;">
                    If you did not request a password reset, you can safely ignore this email.
                  </p>
                </div>
                """.formatted(resetLink, resetLink, resetLink);

        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper =
                    new MimeMessageHelper(mimeMessage, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(email);
            helper.setSubject("Reset your password");
            helper.setText(htmlBody, true);   // true = HTML

            mailSender.send(mimeMessage);

        } catch (MessagingException e) {
            throw new RuntimeException("Failed to send password reset email", e);
        }
    }
}
