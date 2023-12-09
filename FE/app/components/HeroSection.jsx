"use client";
import React, { createElement, useRef, useState } from 'react';
import Image from 'next/image';
import { TypeAnimation } from 'react-type-animation';
import Link from 'next/link';

const HeroSection = () => {
  const [file, setFile] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setUploadSuccess(false); // Reset upload success state when a new file is selected
  };

  const handleUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://127.0.0.1:8000/uploadfile/', {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();
        console.log(data);
        setUploadSuccess(true); // Set upload success state to true
        alert('Tách thông tin thành công, vui lòng tải xuống');
      } catch (error) {
        console.error('Error uploading file:', error);
        setUploadSuccess(false); // Set upload success state to false in case of an error
      }
    }
  };
  const fileInputRef = useRef(null);

  return (
    <section>
      <div className="grid grid-cols-7 sm:grid-cols-12 ">
        <div className="col-span-7 place-self-center text-center sm:text-left">
          <h1 className="text-white mb-4 text-4xl sm:text-5xl font-extrabold ">
            <span className="text-6xl text-white">Ứng dụng lấy thông tin từ căn cước công dân <br /></span>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to bg-pink-600">
              Nhóm 13 bao gồm <br className="mt-2" />{""}
            </span>
            <TypeAnimation
              sequence={[
                "Thắng",
                1000,
                "Nguyên",
                1000,
                "Vũ",
                1000,
                "Thương",
                1000
              ]}
              wrapper="span"
              speed={50}
              style={{ fontSize: '2em', display: 'inline-block' }}
              repeat={Infinity}
            />
          </h1>

          <p className="text-[#ADB7BE] text-base sm:text-xl mb-6 lg:text-1xl">
            Hướng dẫn sử dụng: &nbsp;
            <Link href="/instruction.html">
              <code className=" font-bold">Tại đây</code>
            </Link>
          </p>

          <div>
            {/*<input type="file" onChange={handleFileChange}/>*/}
                <div className="custom-file-input">
              <input type="file" id="fileInput" className="hidden" onChange={handleFileChange} />
            <label htmlFor="fileInput" id="fileInputLabel">
              <span>Choose File</span>
            </label>
            {file && (
              <div htmlFor="fileInput" id="fileInputLabel" style={{ color: 'black', marginLeft:"8px" }}>
                {file.name}
              </div>
            )}
                </div>
            <div className='mt-3'></div>

            <button
              onClick={handleUpload}
              className="px-6 py-3 w-full sm:w-fit rounded-full mr-4 bg-gradient-to-br from-blue-500 to-pink-500 hover:bg-slate-200 text-white"
            >
              Xác nhận ảnh
            </button>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />

 {uploadSuccess && (
          <button className="px-1 py-1 w-full sm:w-fit rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 hover:bg-slate-800 text-white mt-3">
            <a href="http://127.0.0.1:8000/api/download" className="block bg-gradient-to-br from-blue-500 to-pink-500 hover:bg-slate-800 rounded-full px-5 py-2">
              Tải xuống
            </a>
          </button>
        )}

        </div>

        </div>
        <div className="col-span-5 place-self-center mt-4 lg:mt-0">
          <div className="rounded-full bg-[#181818] w-[500px] h-[500px] relative">
            <Image
              src="/images/png-logo-HUS-2.png"
              alt="logo HUS"
              className="absolute transform -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2"
              width={300}
              height={300}
            />
          </div>
        </div>
      </div>
        <style jsx>{`
        .custom-file-input {
          display: flex;
          align-items: center;
        }

        .hidden {
          display: none;
        }

        #fileInputLabel {
          background: #fff;
          color: #000;
          border: 1px solid #000;
          padding: 8px 12px;
          border-radius: 5px;
          cursor: pointer;
          user-select: none;
        }

        #fileInputLabel span {
          display: inline-block;
          margin-right: 8px;
        }

        /* Add any other styles here */
      `}</style>
    </section >
  );
};

export default HeroSection;