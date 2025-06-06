import React, { useState, useEffect } from "react";
import {
  Upload,
  Button,
  Input,
  message,
  Card,
  Typography,
  Row,
  Col,
  List,
  Tabs,
} from "antd";
import {
  UploadOutlined,
  FileTextOutlined,
} from "@ant-design/icons";
import axios from "axios";

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const API_BASE = "http://localhost:8000";

export default function UploadForm() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedBy, setUploadedBy] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [files, setFiles] = useState([]);

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/list-files`);
      setFiles(res.data.files);
    } catch (error) {
      console.error(error);
      message.error("Failed to load uploaded files.");
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleSubmit = async () => {
    if (!selectedFile || !uploadedBy.trim()) {
      message.warning("Please select a file and enter your name.");
      return;
    }
    setLoading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("uploaded_by", uploadedBy);

    try {
      const res = await axios.post(`${API_BASE}/classify/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const newResult = {
        fileName: selectedFile.name,
        path: `/upload/${encodeURIComponent(selectedFile.name)}`,
        fileType: selectedFile.name.split(".").pop().toUpperCase(),
        ...res.data,
      };

      setResult(newResult);
      fetchFiles(); // refresh uploaded list
      message.success("Upload successful!");
    } catch (error) {
      const errorMsg =
        error?.response?.data?.details || error?.message || "Unknown error";
      message.error("Upload failed: " + errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", padding: 24 }}>
      <Card style={{ borderRadius: 12, boxShadow: "0 2px 12px rgba(0,0,0,0.1)" }}>
        <Tabs defaultActiveKey="1" type="line" size="large">
          <TabPane tab="📤 Upload Document" key="1">
            <div style={{ marginBottom: 24 }}>
              <Title level={2} style={{ fontWeight: "bold", marginBottom: 4 }}>
                📤 Document Classifier
              </Title>
              <Text style={{ fontSize: 16, color: "#555" }}>
                Upload your documents for automatic classification
              </Text>
            </div>

            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col xs={24} sm={12}>
                <Input
                  placeholder="Your Name"
                  value={uploadedBy}
                  onChange={(e) => setUploadedBy(e.target.value)}
                  disabled={loading}
                />
              </Col>
              <Col xs={24} sm={12}>
                <Upload
                  beforeUpload={() => false}
                  onChange={({ fileList }) => {
                    if (fileList.length > 0) {
                      setSelectedFile(fileList[fileList.length - 1].originFileObj);
                    } else {
                      setSelectedFile(null);
                    }
                  }}
                  maxCount={1}
                  showUploadList={{ showRemoveIcon: true }}
                  disabled={loading}
                >
                  <Button icon={<UploadOutlined />} disabled={loading}>
                    Select File
                  </Button>
                </Upload>
              </Col>
            </Row>

            <Button
              type="primary"
              onClick={handleSubmit}
              disabled={loading}
              loading={loading}
              block
              style={{ marginBottom: 24 }}
            >
              Submit
            </Button>

            {result && (
              <Card
                type="inner"
                title="📝 Classification Result"
                style={{ marginTop: 24, borderRadius: 8 }}
              >
                <p>
                  <b>📂 File Name:</b>{" "}
                  <a
                    href={`${API_BASE}${result.path}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {result.fileName}
                  </a>
                </p>
                <p>
                  <b>🧾 File Type:</b> {result.fileType}
                </p>
                <p>
                  <b>👤 Uploaded By:</b> {result.uploaded_by}
                </p>
                <p>
                  <b>📅 Uploaded Date:</b> {result.date_uploaded}
                </p>
                <p>
                  <b>📚 Category:</b>{" "}
                  <Input
                    value={result.category}
                    onChange={(e) =>
                      setResult((prev) => ({ ...prev, category: e.target.value }))
                    }
                    style={{ width: 300 }}
                  />
                </p>
                <p>
                  <b>🏷️ Tag:</b>{" "}
                  <Input
                    value={result.tag}
                    onChange={(e) =>
                      setResult((prev) => ({ ...prev, tag: e.target.value }))
                    }
                    style={{ width: 300 }}
                  />
                </p>
              </Card>
            )}
          </TabPane>

          <TabPane tab="📁 Uploaded Files" key="2">
            <List
              itemLayout="horizontal"
              dataSource={files}
              locale={{ emptyText: "No files uploaded yet." }}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<FileTextOutlined style={{ fontSize: 20 }} />}
                    title={
                      <a
                        href={`${API_BASE}${item.path}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {item.name}
                      </a>
                    }
                    description={`Uploaded At: ${item.uploaded_at}`}
                  />
                </List.Item>
              )}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
}
