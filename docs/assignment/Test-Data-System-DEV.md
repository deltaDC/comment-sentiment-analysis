# **BÀI TEST TUYỂN DỤNG** 

**Vị trí:** Chuyên viên Vận hành & Phát triển Hệ thống **Deadline nộp bài:** 3–5 ngày kể từ ngày nhận đề 

**Hình thức nộp:** Git repository (GitHub/GitLab), link demo hoặc zip package 

## **Bối cảnh** 

Nhóm kỹ thuật đang vận hành một hệ thống phân tích dữ liệu mạng xã hội. Một trong những đầu ra quan trọng của hệ thống là **phân loại cảm xúc** của các bình luận người dùng về sản phẩm - phục vụ cho việc đánh giá phản hồi thị trường và nhận diện tín hiệu tiềm năng. 

Bài test này mô phỏng một phần công việc thực tế bạn sẽ đảm nhận. 

## **Yêu cầu** 

### **1. Chuẩn bị dữ liệu** 

- Tự tạo bộ mock data gồm **500–1.000 bình luận** tiếng Việt về sản phẩm xe ô tô. 

- Dữ liệu phải đa dạng, phản ánh thực tế: khen, chê, so sánh, hỏi han, trung tính - không đồng nhất về độ dài và văn phong. 

- Mỗi bình luận phải có nhãn cảm xúc tương ứng: `positive` / `negative` / `neutral` . 

- Lưu dưới định dạng CSV hoặc JSON, có cột/trường rõ ràng. 

- Được phép dùng AI để hỗ trợ sinh dữ liệu, nhưng cần review và đảm bảo nhãn chính xác trước khi đưa vào training. 

### **2. Xây dựng model phân loại cảm xúc** 

Dùng bộ dữ liệu trên để xây dựng một model phân loại cảm xúc văn bản tiếng Việt. 

- Lựa chọn model và phương pháp là quyết định của bạn - cần **giải thích rõ lý do lựa chọn** trong tài liệu đi kèm. 

- Chia dữ liệu thành tập train/validation hợp lý; đánh giá và trình bày kết quả model theo các chỉ số phù hợp với bài toán - nêu rõ lý do chọn chỉ số đó. 

### **3. Microservice API** 

Đóng gói model thành một **REST API** đơn giản bằng **Python** . 

- Endpoint tối thiểu: 

   - `POST /predict` - nhận vào đoạn văn bản, trả về nhãn cảm xúc và confidence score. 

- Xử lý được các trường hợp đầu vào bất thường (chuỗi rỗng, văn bản quá dài, ký tự đặc biệt). 

### **4. Giao diện web** **_(optional)_** 

- Nếu có thời gian, xây dựng giao diện demo đơn giản bằng **Flask** hoặc công cụ tương đương. Chức năng tối thiểu: ô nhập văn bản → submit → hiển thị nhãn cảm xúc + confidence score. Không yêu cầu thiết kế - chạy được và hiển thị đúng kết quả là đủ. 

## **Tiêu chí đánh giá** 

|**Tiêu chí**|**Mô tả**|**Trọng**<br>**số**|
|---|---|---|
|Chất lượng dữ liệu|Đa dạng, có nhãn hợp lý, không lặp lại máy móc|15%|
|Model & phương<br>pháp|Lựa chọn phù hợp, có đánh giá kết quả,**giải thích được quyết**<br>**định**|40%|
|API & xử lý|Code sạch, có xử lý edge case, response chuẩn|30%|
|Tài liệu|README đủ để người khác chạy lại được mà không cần hỏi<br>thêm|15%|



## **Lưu ý** 

- Không yêu cầu độ chính xác tuyệt đối - **cách tiếp cận và lý luận quan trọng hơn kết quả số** . 

- Nếu có giới hạn về tài nguyên (không có GPU), hãy nêu rõ trong tài liệu và trình bày hướng xử lý thay thế hoặc tối ưu nếu có đủ tài nguyên. 

Mọi thắc mắc về **yêu cầu đề bài** , liên hệ thông qua HR - không hỗ trợ giải đáp về kỹ thuật thực hiện. 

_Chúc bạn hoàn thành tốt. Chúng tôi đánh giá cao sự rõ ràng trong tư duy hơn là sự hoàn hảo trong kết quả._ 

