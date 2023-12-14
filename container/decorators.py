from functools import wraps
from flask import request, jsonify

def validate_relationship_input(valid_values=None):
    if valid_values is None:
        valid_values = {
            'causes': ['COMPOUND'],  # Default valid values for 'cause'
            'effects': ['PHENOTYPE']  # Default valid values for 'effect'
        }

    def decorator(func):
        @wraps(func)
        def wrapper():
            data = request.json
            text = data.get('text', '')
            cause = data.get('cause', 'COMPOUND')
            effect = data.get('effect', 'PHENOTYPE')

            # Custom input validation logic
            if not isinstance(text, str) or not text:
                return jsonify({"error": "Invalid input for 'text'. It should be a non-empty string."}), 400

            if cause not in valid_values['causes']:
                return jsonify({"error": f"Invalid value '{cause}' for 'cause'."}), 400
            if effect not in valid_values['effects']:
                return jsonify({"error": f"Invalid value '{effect}' for 'effect'."}), 400

            return func(text, cause, effect)
        return wrapper
    return decorator