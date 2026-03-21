# Kịch bản Demo Gradio + GLiNER2

Dưới đây là **kịch bản demo step-by-step** cho bản **Gradio + GLiNER2**.  
Mục tiêu là demo trong **4–6 phút**, ngắn gọn, rõ ràng, và có **3 khoảnh khắc “wow”**.

GLiNER2 phù hợp cho kịch bản này vì bản Python package hỗ trợ **entity extraction, text classification, structured extraction** trong một model local-first, CPU-first. Gradio phù hợp vì cho phép build **interactive web UI bằng Python**, đặc biệt với `Blocks`, layout, và event listeners. [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/), [\[github.com\]](https://github.com/Yutwizard/skills_Mar2026)

***

## 1) Mục tiêu demo

## Thông điệp chính

> “Đây không phải chatbot. Đây là một **incident intake & triage console** chạy local, dùng **GLiNER2** để biến text lộn xộn thành **metadata + action** ngay lập tức.” [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/)

## 3 điểm người xem phải nhớ

1. **Zero-shot**: thêm label mới ngay lúc demo, **không retrain**. GLiNER2 hỗ trợ extraction theo schema/labels do người dùng đưa vào lúc chạy. [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[github.com\]](https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md)
2. **Multi-task**: cùng một input nhưng ra **entities + classification + incident card có cấu trúc**. [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/)
3. **Local + privacy-first**: dữ liệu không cần đẩy sang API ngoài. GLiNER2 được mô tả là local-first / zero external dependencies ở package docs. [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/)

***

## 2) Chuẩn bị trước khi demo

## Nên chuẩn bị sẵn

* 3 incident fixtures đẹp nhất:
  * `Duplicate charges after rollout`
  * `Login outage for one tenant`
  * `PII leak in logs`
* 1 fixture để **schema mutation** dễ ăn điểm
* 1 fixture để **PII redaction** nhìn thấy rõ
* App mở sẵn ở case đầu tiên
* Cache model/load app xong trước khi trình bày

## Nên bật sẵn trên UI

* Cột trái: case selector + raw text
* Cột giữa: entities, classifications, incident card
* Cột phải: redacted text, routing, schema editor, export actions

***

## 3) Kịch bản demo 5 phút

***

## Bước 1 — Mở đầu: đặt vấn đề

**Thời lượng:** 20–30 giây

### Thao tác

* Mở app ở màn hình chính
* Chưa bấm gì vội

### Lời thoại

> “Team vận hành thường nhận incident dưới dạng **chat, ticket, log** rất lộn xộn. Nếu dùng NER thường thì chỉ ra được vài entity phổ thông. Nếu dùng LLM thì được nhiều hơn, nhưng dễ tốn chi phí, khó giữ format ổn định, và không đẹp cho local/private workflow.  
> Ở đây mình dùng **GLiNER2** để xử lý việc đó theo kiểu **zero-shot, local, schema-driven**.” [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/), [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/)

***

## Bước 2 — Cho xem input “thật”

**Thời lượng:** 30–40 giây

### Thao tác

* Chọn case: **`Duplicate charges after rollout`**
* Cuộn nhanh qua 3 vùng:
  * Chat thread
  * Ticket
  * Logs

### Lời thoại

> “Một case thực tế thường không nằm trong một ô text đẹp đẽ. Nó nằm rải ở nhiều nơi: chat nội bộ, mô tả ticket, và log.  
> Mục tiêu của app này là đọc tất cả phần đó và tự tạo ra **incident metadata** để hỗ trợ triage.”

***

## Bước 3 — Bấm Analyze: “wow” đầu tiên

**Thời lượng:** 45–60 giây

### Thao tác

* Bấm **Analyze**
* Đợi kết quả hiện ở cột giữa và cột phải

### Lời thoại

> “Bây giờ app sẽ chạy **GLiNER2 local** để làm ba việc cùng lúc:
>
> 1. trích entity,
> 2. phân loại severity / owning team / customer impact,
> 3. dựng một incident card có cấu trúc.” [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/)

### Sau khi kết quả hiện ra

Chỉ vào lần lượt:

* `severity = Critical`
* `team = Payments`
* `customer_impact = yes`
* incident card JSON / key fields
* extracted entities như:
  * `service_name`
  * `release_version`
  * `feature_flag`
  * `tenant_id`
  * `exception_type`

### Lời thoại tiếp

> “Điểm khác biệt ở đây là model không chỉ đánh dấu vài entity cơ bản. Nó đang lấy ra đúng những field **nghiệp vụ vận hành** như `feature_flag`, `tenant_id`, `exception_type`, `release_version`.”

***

## Bước 4 — Chỉ vào incident card: “đây là workflow app, không phải wrapper”

**Thời lượng:** 30–40 giây

### Thao tác

* Chỉ vào vùng **Structured Incident Card**
* Mở/tô đậm các field chính

### Lời thoại

> “Nếu đây chỉ là wrapper model, mình sẽ dừng ở chỗ highlight text.  
> Nhưng ở đây output đã trở thành một **incident card có cấu trúc**, tức là thứ có thể đưa tiếp vào dashboard, routing rule, hoặc knowledge base.” [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/)

***

## Bước 5 — PII redaction: “wow” thứ hai

**Thời lượng:** 30–45 giây

### Thao tác

* Chỉ sang cột phải: **Redacted Text**
* So sánh nhanh raw text và redacted text

### Lời thoại

> “Một nhu cầu rất thực tế là phải **che dữ liệu nhạy cảm** trước khi chia sẻ rộng hơn.  
> App này redaction các field như email, account id, customer info, nhưng vẫn giữ lại các field vận hành như service, error signature, version để còn debug.”

### Chốt câu

> “Nghĩa là cùng một pipeline, mình vừa trích thông tin để triage, vừa chuẩn bị bản text an toàn hơn để dùng tiếp.”

***

## Bước 6 — Routing & filter chips: “đây là action, không chỉ extraction”

**Thời lượng:** 30–40 giây

### Thao tác

* Chỉ vào:
  * `Route to: Payments Oncall`
  * `Escalate: Critical`
  * filter chips như `service`, `exception_type`, `environment`

### Lời thoại

> “Điểm mình muốn nhấn mạnh là **output dẫn đến action**.  
> App không chỉ nói ‘tôi thấy các entity này’.  
> Nó còn gợi ý **route case đi đâu**, mức độ ưu tiên, và tạo sẵn các **filter chips** để tìm incident tương tự.”

***

## Bước 7 — Baseline compare: “tại sao không dùng NER thường?”

**Thời lượng:** 35–45 giây

### Thao tác

* Mở tab / panel **Baseline Compare**
* So sánh `Traditional/regex baseline` với `GLiNER2`

### Lời thoại

> “Mình có để một baseline đơn giản để cho thấy khác biệt.  
> Baseline thường bắt được vài thứ kiểu email, date, maybe id pattern.  
> Nhưng các entity nghiệp vụ như `feature_flag`, `rollback_reason`, `blast_radius`, `customer_impact signal` thì nó không hiểu.”

### Chốt câu

> “Đây là chỗ **zero-shot NER/IE** thực sự có giá trị: label thay đổi theo business, không thể retrain mỗi tuần.”

***

## Bước 8 — Live schema mutation: “wow” lớn nhất

**Thời lượng:** 45–60 giây

### Thao tác

* Sang **Schema Configuration** tab.
* Ở bảng **Entity Labels**, cuộn xuống cuối và thêm một dòng mới:
  * Label Name: `Financial Impact`
  * Description: `Monetary values associated with the incident cost or loss.`
  * Active: `Checked`
* Bấm **Save Configuration**.
* Quay lại **Incident Triage** tab.
* Đảm bảo đang chọn case **`Duplicate charges after rollout`**.
* Bấm **Run Analysis**.

### Lời thoại

> “Bây giờ mình sẽ thêm một field nghiệp vụ cực kỳ quan trọng ngay lúc demo: **`Financial Impact`**.  
> Thông thường, team kỹ thuật chỉ quan tâm đến log và code, nhưng team quản lý sẽ muốn biết ngay thiệt hại về tiền là bao nhiêu.”

### Khi kết quả hiện

* Chỉ vào phần **GLiNER2 Extracted Intelligence**: label `Financial Impact` đã xuất hiện và highlight số tiền `$4,500`.
* Chỉ vào **Incident Card JSON** (nếu đang mở): field mới đã được trích xuất vào cấu trúc dữ liệu.

### Chốt câu thật rõ

> “Mọi người thấy đó: **Không retrain. Không deploy lại model.**  
> Mình chỉ vừa định nghĩa thêm một ‘khái niệm’ mới vào schema, và GLiNER2 lập tức hiểu và trích xuất nó từ đoạn chat lộn xộn ban nãy.” [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[github.com\]](https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md)

### Câu punchline

> “Đây là sức mạnh của **Zero-shot Information Extraction**: Model đủ thông minh để hiểu label mới dựa trên ngữ nghĩa (semantics), giúp hệ thống thích nghi với yêu cầu business thay đổi chỉ trong vài giây.”

***

## Bước 9 — Optional hybrid mode: “không anti-LLM, mà đặt LLM đúng chỗ”

**Thời lượng:** 30–40 giây

### Thao tác

* Bấm **Generate LLM-ready brief**
* Hiện ra prompt/brief ngắn từ redacted structured output

### Lời thoại

> “Nếu vẫn muốn dùng LLM, mình sẽ không dùng nó cho extraction ban đầu.  
> Mình dùng **GLiNER2 để extract + redact trước**, rồi mới tạo một brief sạch để đưa cho LLM viết timeline hoặc executive summary.”

### Chốt câu

> “Tức là model nhỏ chuyên extraction làm đúng việc của nó, còn model lớn chỉ làm reasoning ở bước sau.” [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/), [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/)

***

## Bước 10 — Kết thúc: tổng kết 3 ý

**Thời lượng:** 20–30 giây

### Lời thoại

> “Tóm lại, demo này cho thấy 3 điều:
>
> 1. **GLiNER2 không chỉ là NER**, mà là một lớp information extraction có thể đưa vào workflow.
> 2. Nó **local-first, zero-shot, schema-driven**, nên hợp với dữ liệu nhạy cảm và label nghiệp vụ thay đổi nhanh.
> 3. Với Gradio, team không có frontend dev vẫn có thể build được một console đủ đẹp và đủ tương tác để demo hoặc pilot nội bộ.” [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/), [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/), [\[github.com\]](https://github.com/Yutwizard/skills_Mar2026), [\[github.com\]](https://github.com/VoltAgent/awesome-agent-skills/compare/VoltAgent:380436a...zakstam:8185f06.patch)

***

## 4) 3 câu ngắn để chốt sau demo

Bạn có thể chọn 1 trong 3 câu này để kết:

## Cách chốt 1

> “LLM rất mạnh, nhưng không phải bước nào trong pipeline cũng nên dùng LLM. Extraction có cấu trúc, local, nhiều label động — đó là chỗ GLiNER2 đẹp hơn.” [\[smartscope.blog\]](https://smartscope.blog/en/generative-ai/github-copilot/github-copilot-skills-guide/), [\[mkabumattar.com\]](https://mkabumattar.com/devtips/post/github-copilot-agent-skills-setup/)

### Cách chốt 2

> “Nếu taxonomy business đổi từng sprint, thì zero-shot schema mutation không phải luxury — nó là requirement.”

### Cách chốt 3

> “Điểm ‘wow’ không phải là model trả lời hay. Điểm ‘wow’ là từ một mớ text lộn xộn, app tạo ra được **metadata + routing + redaction + incident card** để team hành động ngay.”

***

## 5) Backup script nếu thời gian chỉ còn 2 phút

Nếu bạn bị cắt thời gian, chỉ giữ 4 bước này:

1. **Mở case**
    > “Đây là incident gồm chat + ticket + logs.”

2. **Analyze**
    > “GLiNER2 local trích entity, classify severity/team, và dựng incident card.”

3. **Redaction**
    > “Cùng pipeline đó, app che PII nhưng giữ entity phục vụ debug.”

4. **Thêm label mới live**
    > “Mình thêm `rollback_reason` ngay lúc demo, rerun, có kết quả luôn — không retrain.”

Chỉ cần 4 bước này là vẫn đủ “wow”.

***

## 6) Nếu có lỗi trong lúc demo, nói gì cho gọn?

## Trường hợp UI lag / model chậm

> “Mình đang chạy local để giữ privacy và để thể hiện đúng deployment story, nên lần đầu load có thể chậm hơn một chút.”

## Trường hợp một field extract chưa đẹp

> “Đây là lúc zero-shot thể hiện đúng bản chất: mình có thể tinh chỉnh label description hoặc threshold thay vì phải retrain cả pipeline.”

## Trường hợp baseline nhìn chưa đủ chênh

> “Baseline ở đây chỉ để minh hoạ rằng regex / NER thường không hiểu business entities. Giá trị chính là schema mutation + structured workflow.”

***

Nếu bạn muốn, bước tiếp theo mình có thể viết tiếp cho bạn một bản **MC script hoàn chỉnh 1:1**, tức là:

* **mỗi click nói câu gì**
* **mỗi vùng trên màn hình chỉ vào đâu**
* **thậm chí có cả bản 3 phút và bản 5 phút**

để bạn mang đi tập luôn.
