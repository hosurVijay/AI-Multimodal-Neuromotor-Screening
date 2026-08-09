package com.neurologicaldisorder.Service;

import com.neurologicaldisorder.Dto.LoginRequest;
import com.neurologicaldisorder.Dto.LoginResponse;
import com.neurologicaldisorder.DTO.RegisterRequest;
import com.neurologicaldisorder.DTO.RegisterResponse;
import com.neurologicaldisorder.Exception.ResourceAlreadyExistsException;
import com.neurologicaldisorder.Model.PasswordResetToken;
import com.neurologicaldisorder.Model.Role;
import com.neurologicaldisorder.Model.User;
import com.neurologicaldisorder.Repository.PasswordResetTokenRepo;
import com.neurologicaldisorder.Repository.UserRepo;
import com.neurologicaldisorder.Security.JwtService;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;

import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final PasswordResetTokenRepo passwordResetTokenRepo;

    private final EmailService emailService;

    private final AuthenticationManager authenticationManager;

    private final UserRepo userRepo;

    private final JwtService jwtService;

    private final PasswordEncoder passwordEncoder;


    // =========================
    // LOGIN
    // =========================

    public LoginResponse login(LoginRequest request) {

        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );

        User user = userRepo.findByEmail(request.getEmail())
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        String token = jwtService.generateToken(
                user.getUsername(),
                user.getEmail(),
                user.getRole().name()
        );

        return LoginResponse.builder()
                .accessToken(token)
                .tokenType("Bearer")
                .expiresIn(jwtService.getJwtExpiration())
                .username(user.getUsername())
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }


    // =========================
    // REGISTER
    // =========================

    public RegisterResponse register(
            RegisterRequest request) {

        if (userRepo.existsByUsername(request.getUsername())) {

            throw new ResourceAlreadyExistsException(
                    "Username already exists"
            );
        }

        if (userRepo.existsByEmail(request.getEmail())) {

            throw new ResourceAlreadyExistsException(
                    "Email already registered"
            );
        }

        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())

                // IMPORTANT:
                // Never save plain-text passwords
                .password(
                        passwordEncoder.encode(
                                request.getPassword()
                        )
                )

                // Public registration creates DOCTOR
                .role(Role.DOCTOR)

                .isActive(true)

                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())

                .build();

        User savedUser = userRepo.save(user);

        return RegisterResponse.builder()
                .userId(savedUser.getUserId())
                .username(savedUser.getUsername())
                .email(savedUser.getEmail())
                .role(savedUser.getRole().name())
                .message("User registered successfully")
                .build();
    }
    @Transactional
    public void forgotPassword(String email) {

        User user = userRepo.findByEmail(email)
                .orElse(null);

        /*
         * Don't reveal whether an email exists.
         *
         * If the email doesn't exist, simply return.
         */
        if (user == null) {
            return;
        }

        // Remove previous reset tokens
        passwordResetTokenRepo
                .deleteByUser_UserId(user.getUserId());

        String token = UUID.randomUUID().toString();

        PasswordResetToken resetToken =
                PasswordResetToken.builder()
                        .token(token)
                        .user(user)
                        .expiryDate(
                                LocalDateTime.now()
                                        .plusMinutes(15)
                        )
                        .used(false)
                        .build();

        passwordResetTokenRepo.save(resetToken);

        emailService.sendPasswordResetEmail(
                user.getEmail(),
                token
        );
    }

    public void resetPassword(
            String token,
            String newPassword) {

        PasswordResetToken resetToken =
                passwordResetTokenRepo
                        .findByToken(token)
                        .orElseThrow(() ->
                                new RuntimeException(
                                        "Invalid reset token"
                                )
                        );

        if (resetToken.isUsed()) {

            throw new RuntimeException(
                    "Reset token has already been used"
            );
        }

        if (resetToken.getExpiryDate()
                .isBefore(LocalDateTime.now())) {

            throw new RuntimeException(
                    "Reset token has expired"
            );
        }

        User user = resetToken.getUser();

        user.setPassword(
                passwordEncoder.encode(newPassword)
        );

        user.setUpdatedAt(
                LocalDateTime.now()
        );

        userRepo.save(user);

        // Make token single-use
        resetToken.setUsed(true);

        passwordResetTokenRepo.save(resetToken);
    }
}