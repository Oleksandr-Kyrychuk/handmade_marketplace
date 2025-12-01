import { CategoryApi } from "./API/category-api";
import { CategoryService } from "./Services/category-services";

const categoryApi = new CategoryApi();
const categoryService = new CategoryService(categoryApi);

export {categoryService}