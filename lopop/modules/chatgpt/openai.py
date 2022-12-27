import openai

openai.api_key = "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"  # 这里放入你的key


def get_response_from_openai(prompt, temperature=0.5):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        temperature=temperature,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return completions.choices[0].text

# if __name__ == '__main__':
#     prompt = ''
#     response = ''
#     while (True):
#         prompt = f"{response}{input()}"
#         # print(prompt)
#         tmp = generate_response(prompt)
#         response += tmp
#         print(tmp)
