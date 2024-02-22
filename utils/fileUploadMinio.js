const Minio = require('minio');
const fs = require('fs');
const util = require('util');
const unlinkFile = util.promisify(fs.unlink);

const fileUpload = async (objectName, filePath) => {
    return new Promise(async (resolve, reject) => {
        const minioClient = new Minio.Client({
            endPoint: process.env.MINIO_URI,
            port: Number(process.env.MINIO_PORT),
            useSSL: false,
            accessKey: process.env.MINIO_ACCESS_KEY,
            secretKey: process.env.MINIO_SECRET_KEY,
        });

        const bucketName = process.env.MINIO_BUCKET_NAME;

        try {
            const exists = await minioClient.bucketExists(bucketName);

            if (exists) {
                console.log('Bucket already exists.');
                const etag = await minioClient.fPutObject(bucketName, objectName, filePath, {});
                console.log('Document uploaded successfully. ETag:', etag);

                // const presignedUrl = await minioClient.presignedGetObject(bucketName, objectName, 7 * 24 * 60 * 60); // URL valid for 10 years
                const minioUrl = "http://" + process.env.MINIO_URI + ':' + process.env.MINIO_PORT;
                const presignedUrl = await setFileUrl(minioUrl, bucketName, objectName);
                await unlinkFile(filePath);
                resolve(presignedUrl);
            } else {
                await minioClient.makeBucket(bucketName, process.env.MINIO_REGION);
                console.log('Bucket created successfully.');
                const etag = await minioClient.fPutObject(bucketName, objectName, filePath, {});
                console.log('Document uploaded successfully. ETag:', etag);

                // const presignedUrl = await minioClient.presignedGetObject(bucketName, objectName, 7 * 24 * 60 * 60); // URL valid for 7 days
                const minioUrl = "http://" + process.env.MINIO_URI + ':' + process.env.MINIO_PORT;
                const presignedUrl = await setFileUrl(minioUrl, bucketName, objectName);
                await unlinkFile(filePath);
                resolve(presignedUrl);
            }
        } catch (err) {
            await unlinkFile(filePath);
            console.log('Error:', err);
            reject(err);
        }
    });
};

const setFileUrl = async (minioPort, bucketName, objectPath) => {
    return minioPort + '/' + bucketName + '/' + objectPath;
}

module.exports = { fileUpload };