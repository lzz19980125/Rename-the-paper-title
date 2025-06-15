import os
import re
from PyPDF2 import PdfFileReader
import fitz  # PyMuPDF


def extract_title_from_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            pdf = PdfFileReader(f)
            if pdf.isEncrypted:
                # 尝试用空密码解密
                pdf.decrypt('')
            info = pdf.getDocumentInfo()
            if info:
                title = info.get('/Title', '')
                if title:
                    return title
    except Exception as e:
        print(f"读取 {pdf_path} 的元数据时出错: {e}")
    return None


def extract_title_from_content(pdf_path, elsevier_journal_keywords):
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None
        page = doc[0]
        spans = []
        blocks = page.get_text("dict").get("blocks", [])

        # 收集所有文本块
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:  # 只保留非空文本
                            bbox = span["bbox"]
                            spans.append({
                                "text": text,
                                "size": span["size"],
                                "y0": bbox[1],
                                "x0": bbox[0]
                            })

        if not spans:
            return None

        # 获取所有字体大小并排序
        sizes = sorted(set(span["size"] for span in spans), reverse=True)
        if len(sizes) < 2:
            return None

        # 获取最大字体的文本
        largest_spans = [span for span in spans if span["size"] == sizes[0]]
        largest_spans.sort(key=lambda s: (s["y0"], s["x0"]))
        largest_text = ' '.join(span["text"] for span in largest_spans)

        # 检查特殊情况
        should_use_second_size = False

        # 情况1: arxiv 或 peer review
        if 'arxiv' in largest_text.lower() or 'peer review' in largest_text.lower():
            should_use_second_size = True

        # 情况2: IEEE Transactions (通常只有1-2个大写字母)
        if len(largest_text.strip()) <= 2 and largest_text.isupper():
            should_use_second_size = True

        # 情况3: Elsevier 期刊名
        largest_text_lower = largest_text.lower()
        for keyword in elsevier_journal_keywords:
            if keyword.lower() in largest_text_lower:
                should_use_second_size = True
                break

        if should_use_second_size:
            second_largest_spans = [span for span in spans if span["size"] == sizes[1]]
            second_largest_spans.sort(key=lambda s: (s["y0"], s["x0"]))
            return ' '.join(span["text"] for span in second_largest_spans)

        return largest_text

    except Exception as e:
        print(f"处理 {pdf_path} 的内容时出错: {e}")
        return None
    finally:
        if 'doc' in locals():
            doc.close()


def clean_filename(title):
    """清理文件名，移除非法字符"""
    if not title:
        return None
    # 先将冒号替换为空格
    title = title.replace(':', ' ')
    # 规范化空格（将多个连续空格替换为单个空格）
    title = ' '.join(title.split())
    # 替换Windows文件系统中的其他非法字符
    cleaned = re.sub(r'[\\/*?"<>|]', '_', title.strip())
    # 如果末尾是 "_1"，则删除
    if cleaned.endswith('_1'):
        cleaned = cleaned[:-2]
    # 限制文件名长度
    return cleaned[:200]


def get_unique_filename(directory, base_name, ext):
    """生成唯一的文件名，避免重名"""
    new_name = f"{base_name}.{ext}"
    target_path = os.path.join(directory, new_name)
    if os.path.exists(target_path):
        print(f"警告：检测到重名文件 '{new_name}'")
        print(f"现有文件: {os.path.getsize(target_path)} 字节")

    counter = 1
    while os.path.exists(target_path):
        new_name = f"{base_name} ({counter}).{ext}"
        target_path = os.path.join(directory, new_name)
        counter += 1
    return new_name


def main(elsevier_journal_keywords):
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python script.py <目录路径>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是有效的目录。")
        sys.exit(1)

    # 用于跟踪已使用的新文件名
    used_names = set()

    # 处理目录中的所有PDF文件
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            print(f"正在处理: {filename}")

            # 首先尝试从元数据中提取标题
            title = extract_title_from_metadata(pdf_path)

            # 如果元数据中没有标题，则尝试从内容中提取
            if not title:
                print("元数据中没有标题，正在从内容中提取...")
                title = extract_title_from_content(pdf_path, elsevier_journal_keywords)

            # 如果无法提取标题，跳过此文件
            if not title:
                print(f"无法从 {filename} 中提取标题。跳过。")
                continue

            # 清理并验证提取的标题
            cleaned_title = clean_filename(title)
            if not cleaned_title:
                print(f"从 {filename} 提取的标题无效。跳过。")
                continue

            # 生成不重复的新文件名
            base_name = cleaned_title
            counter = 1
            new_name = f"{base_name}.pdf"
            while new_name in used_names:
                new_name = f"{base_name} ({counter}).pdf"
                counter += 1

            used_names.add(new_name)

            # 重命名文件
            try:
                os.rename(pdf_path, os.path.join(directory, new_name))
                print(f"已将 '{filename}' 重命名为 '{new_name}'")
            except Exception as e:
                print(f"重命名 {filename} 时出错: {e}")


if __name__ == "__main__":
    journal_keywords = ["Knowledge-Based Systems", "Information Sciences", "Reliability Engineering and System Safety", "Neural Networks",
                                 "Expert Systems with Applications", "Engineering Applications of Artificial Intelligence", "Neurocomputing", "Measurement",
                                 "Advanced Engineering Informatics", "ISA Transactions", "Computers in Industry", "Future Generation computer systems", "Pattern Recognition",
                                 "Information Fusion", "Information Processing and Management", "Applied Soft Computing", "Ocean Engineering", "Applied Ocean Research",
                                 "Robotics and Autonomous Systems", "Robotics and Computer-Integrated Manufacturing", "Journal of Ocean Engineering and Science",
                                 "International Journal of Mechanical Sciences", "Swarm and Evolutionary Computation", "computer methods in applied mechanics and engineering",
                                 "Control Engineering Practice", "Ocean Modelling", "Defence Technology", "Physica A", "Sensors", "remote sensing", "Nuclear Engineering and Design",
                                 "Computers Industrial Engineering &"]
    main(journal_keywords)