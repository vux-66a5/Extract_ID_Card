"use client";
import React, { createElement, useRef, useState } from 'react';
import Image from 'next/image';
import { TypeAnimation } from 'react-type-animation';
import Link from 'next/link';


const HeroSection = () => {
  
  const [file, setFile] = useState(null);
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
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
        alert('Đã tải ảnh lên thành công');
      } catch (error) {
        console.error('Error uploading file:', error);
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
            <Link href="/howtouse.txt">
              <code className=" font-bold">Tại đây</code>
            </Link>
          </p>

          <div>
            <input type="file" onChange={handleFileChange} />
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

<button
  className="px-1 py-1 w-full sm:w-fit rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 hover:bg-slate-800 text-white mt-3"
>
  <a href="http://127.0.0.1:8000/api/download" className="block bg-gradient-to-br from-blue-500 to-pink-500 hover:bg-slate-800 rounded-full px-5 py-2">
    Tải xuống
  </a>
</button>

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
    </section >
  );
};

export default HeroSection;