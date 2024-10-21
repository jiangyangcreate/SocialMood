import subprocess
import sys
import nltk


def install_requirements():
    print("正在安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def install_browser():
    print("正在安装浏览器...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])

def download_nltk_data():
    print("正在下载NLTK词典文件...")
    nltk.download('vader_lexicon')

def download_qwen2_model():
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        print("正在下载Qwen2大模型（7B）...")
        model_name = "Qwen/Qwen2.5-7B-Instruct"

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use mixed precision
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        prompt = "请回复：你好，我是Qwen2大模型，有什么可以帮您的吗？"
        messages = [
            {"role": "system", "content": "when the user provides a sentence, respond only with the sentiment score of that sentence, ranging from -1 to 1. No additional information or context should be provided."},
            {"role": "user", "content": prompt}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        print('Qwen2大模型（7B）响应:', response)
    except Exception as e:
        print(f"跳过下载Qwen2大模型（7B），出现错误：{e}")

def main():
    try:
        install_requirements()
        install_browser()
        download_nltk_data()
        download_qwen2_model()
        print("所有安装步骤已完成！")
    except subprocess.CalledProcessError as e:
        print(f"安装过程中出现错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
