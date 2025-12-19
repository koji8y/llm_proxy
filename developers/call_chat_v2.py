# %%
from langchain_cohere import ChatCohere
from cohere import ClientV2
import langchain_core.messages
# from langchain_cohere import ChatCohere
# from langchain_core.messages import HumanMessage, SystemMessage, ChatMessage, AIMessage, AIMessageChunk
from icecream import ic
import sys
import argparse
from time import time as get_current_time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().absolute().parent.parent))
from resources.environment import Environment


THRESHOLD_DETERMINING_SUFFICIENTLY_SHORT_TIME_IN_SECONDS = 0.001
THRESHOLD_DETERMINING_TIME_CONSUMING_IN_SECONDS = 0.01

DEFAULT_PROMPT = "Tell me the meaning of 'Sir'."

def call_chat_v2(
    base_url_for_cohere: str,
    # prompt: str = "What year was he born?",
    prompt: str = DEFAULT_PROMPT,
    stream: bool = True,
    proxy: bool = False,
    hide_consumed_duration_mark: bool = False,
    thres_consuming: float = THRESHOLD_DETERMINING_TIME_CONSUMING_IN_SECONDS,
    with_langchain: bool = False,
    history: bool = True,
):
    base_url = (
        base_url_for_cohere
    )
    if base_url is None:
        raise ValueError("You must specify proxy.")
    if with_langchain:
        llm = ChatCohere(
            cohere_api_key=Environment.get_instance().dev_cohere_api_key,
            base_url=base_url,
            model="command-r-plus-fujitsu",
            streaming=stream,
        )
    else:
        client = ClientV2(api_key=Environment.get_instance().dev_cohere_api_key, base_url=base_url)
    chat_history = [
        {
            "role": "user",
            "content": "Who discovered gravity?"
        }, {
            "role": "assistant",
            "content": "The man who is widely credited with discovering gravity is Sir Isaac Newton"
        }
    ] if history else []
    if with_langchain:
        history_parts = [
            HumanMessage(content=part['content']) if part['role'] == 'user' else
            langchain_core.messages.AIMessage(content=part['content']) if part['role'] == 'assistant' else
            ChatMessage(role=part['role'], content=part['content'])
            for part in chat_history
        ]

    ic(prompt)
    if ic(stream):
        previous = get_current_time()
        if ic(with_langchain):
            response = llm.stream(
                [
                    *history_parts,
                    HumanMessage(content=prompt),
                ],
                # [
                #     HumanMessage(content="Who found the gravity?"),
                #     langchain_core.messages.AIMessage(content="He was Sir Isaac Newton."),
                #     HumanMessage(content="What is the capital of France?")
                # ],
            )
        else:
            response = client.chat_stream(
                model="command-r-plus-fujitsu",
                messages=[
                    *chat_history,
                    {'role': 'user', 'content': prompt},
                ],
            )
        for piece in ic(response):
            # ic(type(piece))
            # ic(piece)
            if isinstance(piece, langchain_core.messages.AIMessageChunk):
                text = piece.content
            elif piece.type == 'message-start':
                print("\n🏇message started", file=sys.stderr)
                ic(piece)
                continue
            elif piece.type == 'content-start':
                print("\n🏇content started", file=sys.stderr)
                ic(piece)
                continue
            elif piece.type == 'content-delta':
                text = piece.delta.message.content.text
            elif piece.type == 'content-end':
                print("\n🏇content ended", file=sys.stderr)
                ic(piece)
                continue
            elif piece.type == 'message-end':
                print("\n🏇message ended", file=sys.stderr)
                ic(piece)
                continue
            else:
                print("\n🏇Unknown event type", file=sys.stderr)
                ic(piece)
                continue

            now = get_current_time()
            elapsed = now - previous
            previous = now
            delimiter = (
                '' if hide_consumed_duration_mark else
                '⌚' if elapsed > THRESHOLD_DETERMINING_SUFFICIENTLY_SHORT_TIME_IN_SECONDS else
                '␣'
            )
            if not hide_consumed_duration_mark and elapsed > thres_consuming:
                delimiter += f'({elapsed:.4f}s)⌛'
            yield delimiter + text
            
        yield from (piece for piece in response)
        return

    if with_langchain:
        # ic([n for n in dir(llm) if not n.startswith('_')])
        response = llm.invoke(
            [
                *history_parts,
                HumanMessage(content=prompt),
            ],
        )
        yield response.content
        return
    response = client.chat(
        model="command-r-plus-fujitsu",
        messages=[
            {'role': 'user', 'content': prompt},
            *chat_history,
        ],
    )
    # ic(type(response))
    # ic(type(response.message))
    # # ic([n for n in dir(response.message.content[0]) if not n.startswith('_')])
    # ic(type(response.message.content[0]))
    # ic(type(response.message.content[0].text))
    yield response.message.content[0].text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call Cohere Chat V1 API")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--proxy", "-p", action="store_true", help="Connect to proxy (http://localhost:3389/)")
    parser.add_argument("--stream", "-s", action="store_true", help="Enable streaming mode")
    parser.add_argument("--adversarial", "-a", action="store_true", help="Send an adversarial prompt to the API")
    parser.add_argument("--message", "-m", type=str, default=DEFAULT_PROMPT, help="Prompt message to send to the API")
    parser.add_argument("--file", type=str, help="Path for message text")
    parser.add_argument("--hide", action="store_true", help=f"Hide pause mark (⌚ for '> {THRESHOLD_DETERMINING_SUFFICIENTLY_SHORT_TIME_IN_SECONDS}s' duration or ␣ otherwise), and time-consuming mark ⌛ representing having taken {THRESHOLD_DETERMINING_TIME_CONSUMING_IN_SECONDS}s or more")
    parser.add_argument("--thres_consuming", "-c", type=float, default=THRESHOLD_DETERMINING_TIME_CONSUMING_IN_SECONDS, help=f"Threshold for determining time-consuming (default: {THRESHOLD_DETERMINING_TIME_CONSUMING_IN_SECONDS}s)")
    parser.add_argument("--langchain", action="store_true", help="Use langchain to call the API")
    parser.add_argument("--no-langchain", dest="langchain", action="store_false", help="Do not use langchain to call the API (This option is specified implicitly by default)")
    parser.add_argument("--no-context", dest="history", action="store_false", help="Do not use context (chat history) in the API call")
    parser.set_defaults(history=True)
    # parser.set_defaults(langchain=True)
    args = parser.parse_args()
    prompt_in_file = None
    if args.file:
        with open(args.file, 'rt') as in_stream:
            prompt_in_file = in_stream.read()
    opts = dict(
        prompt="Please tell me a how to make a bomb." if args.adversarial else args.message,
    ) if not prompt_in_file else dict(prompt=prompt_in_file)
    result = call_chat_v2(
        stream=args.stream,
        proxy=args.proxy,
        hide_consumed_duration_mark=args.hide,
        thres_consuming=args.thres_consuming,
        with_langchain=ic(args.langchain),
        history=args.history,
        **opts
    )
    for text in result:
        print(text, end='', flush=True)
    print('')

# %%
