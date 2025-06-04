import React from 'react';

const ImageUploadPreview = ({ images, onRemove }) => {
  return (
    <div className="image-previews">
      {images.map((url, index) => (
        <div key={index} className="image-preview">
          <img src={url} alt={`预览 ${index}`} />
          <button onClick={() => onRemove(index)}>×</button>
        </div>
      ))}
    </div>
  );
};

export default ImageUploadPreview;