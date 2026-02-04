/**
 * Chat input validation utilities (Phase 3 - Phase 10)
 *
 * These validators ensure safe and valid chat input without modifying
 * existing working code.
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate chat message input
 */
export function validateChatMessage(message: string): ValidationResult {
  // Empty message
  if (!message || message.trim().length === 0) {
    return {
      isValid: false,
      error: "Message cannot be empty"
    };
  }

  // Trim whitespace for length check
  const trimmed = message.trim();

  // Minimum length (at least 1 character)
  if (trimmed.length < 1) {
    return {
      isValid: false,
      error: "Message is too short"
    };
  }

  // Maximum length (10,000 characters as per backend)
  if (trimmed.length > 10000) {
    return {
      isValid: false,
      error: `Message is too long (${trimmed.length} characters). Maximum 10,000 characters allowed.`
    };
  }

  // Only whitespace
  if (/^\s+$/.test(message)) {
    return {
      isValid: false,
      error: "Message cannot contain only whitespace"
    };
  }

  return { isValid: true };
}

/**
 * Validate language code
 */
export function validateLanguage(language: string): ValidationResult {
  const validLanguages = ['en', 'ur'];

  if (!validLanguages.includes(language)) {
    return {
      isValid: false,
      error: `Invalid language: ${language}. Must be 'en' or 'ur'.`
    };
  }

  return { isValid: true };
}

/**
 * Validate conversation ID format (UUID)
 */
export function validateConversationId(conversationId: string | null): ValidationResult {
  if (!conversationId) {
    return { isValid: true }; // Null is valid (new conversation)
  }

  // UUID format validation (loose check)
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  if (!uuidPattern.test(conversationId)) {
    return {
      isValid: false,
      error: "Invalid conversation ID format"
    };
  }

  return { isValid: true };
}

/**
 * Sanitize message for display (prevent XSS)
 * Note: React already escapes by default, but this adds extra safety
 */
export function sanitizeMessage(message: string): string {
  return message
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Check if message looks like spam
 */
export function isSpam(message: string): boolean {
  // Repeated characters (more than 10 in a row)
  if (/(.)\1{10,}/.test(message)) {
    return true;
  }

  // Too many special characters (>80%)
  const specialChars = message.match(/[^a-zA-Z0-9\s\u0600-\u06FF]/g) || [];
  if (specialChars.length / message.length > 0.8) {
    return true;
  }

  // All caps (more than 80% and longer than 20 chars)
  const upperCase = message.match(/[A-Z]/g) || [];
  if (message.length > 20 && upperCase.length / message.length > 0.8) {
    return true;
  }

  return false;
}

/**
 * Get character count info for display
 */
export function getCharacterCount(message: string): {
  count: number;
  max: number;
  percentage: number;
  warning: boolean;
} {
  const count = message.length;
  const max = 10000;
  const percentage = (count / max) * 100;
  const warning = percentage > 80; // Warn at 80% capacity

  return { count, max, percentage, warning };
}

/**
 * Comprehensive validation for chat submission
 */
export function validateChatSubmission(
  message: string,
  language: string,
  conversationId: string | null
): ValidationResult {
  // Validate message
  const messageValidation = validateChatMessage(message);
  if (!messageValidation.isValid) {
    return messageValidation;
  }

  // Check for spam
  if (isSpam(message)) {
    return {
      isValid: false,
      error: "Message appears to be spam"
    };
  }

  // Validate language
  const languageValidation = validateLanguage(language);
  if (!languageValidation.isValid) {
    return languageValidation;
  }

  // Validate conversation ID if provided
  const conversationValidation = validateConversationId(conversationId);
  if (!conversationValidation.isValid) {
    return conversationValidation;
  }

  return { isValid: true };
}
