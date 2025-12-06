// import React from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

export default function UploadComponents() {
  const onDrop = async (acceptedFiles) => {
    const fd = new FormData();
    fd.append("file", acceptedFiles[0]);

    const res = await axios.post("http://localhost:8000/upload", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    console.log("Uploaded:", res.data);
    alert("Uploaded Successfully!");
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div
      {...getRootProps()}
      className="border-2 border-dashed p-6 text-center rounded-md cursor-pointer"
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop your file here…</p>
      ) : (
        <p>Drag & drop a file here or click to upload</p>
      )}
    </div>
  );
}
