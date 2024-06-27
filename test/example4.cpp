 void RobertsOperatorParallelCollapse(cv::Mat img, cv::Mat out){
    #pragma acc parallel
    {
        int i = 0, j = 0;
        #pragma acc loop private(i,j) collapse(2)
        for (i = 0; i < img.cols - 1; ++i){

            for (j = 0; j < img.rows - 1; ++j){
                out.at<unsigned char>(j, i) = (std::abs(img.at<unsigned char>(j, i) - img.at<unsigned char>(j + 1, i + 1)) + std::abs(img.at<unsigned char>(j,i + 1) - img.at<unsigned char>(j + 1, i))) / 2;
            }
        }
    }
}