"""Use your own model name. Run it like this:

    CLIBRIDGE_ALIASES="inhouse=claude-code/sonnet" python examples/06_your_own_model_name.py
"""

import litellm

reply = litellm.completion(model="inhouse", messages=[{"role": "user", "content": "Say hello!"}])
print(reply.choices[0].message.content)
