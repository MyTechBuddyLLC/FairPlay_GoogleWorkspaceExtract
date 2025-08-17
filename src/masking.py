"""
Handles the masking of Personally Identifiable Information (PII) in user data.
"""
import copy

def mask_user_profile(user_profile: dict, role: str, masking_level: str) -> dict:
    """
    Masks PII in a user profile based on the specified role and masking level.

    Args:
        user_profile: The original user profile dictionary from the Google API.
        role: The user's role ('TEACHER' or 'STUDENT').
        masking_level: The configured PII masking level ('none', 'students_only', 'all').

    Returns:
        A new user profile dictionary, which is masked if the conditions are met.
        Returns a deep copy of the original profile if no masking is required.
    """
    profile_copy = copy.deepcopy(user_profile)
    user_id = profile_copy.get('id')

    if not user_id:
        # Cannot mask without a stable ID, return as is
        return profile_copy

    should_mask = (
        (masking_level == 'all') or
        (masking_level == 'students_only' and role == 'STUDENT')
    )

    if not should_mask:
        return profile_copy

    # Apply masking
    profile_copy['name']['fullName'] = f"user_{user_id}"
    profile_copy['emailAddress'] = f"user_{user_id}@masked.local"
    if 'photoUrl' in profile_copy:
        profile_copy['photoUrl'] = '' # Remove photo URL

    return profile_copy
