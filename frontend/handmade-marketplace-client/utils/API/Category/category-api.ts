import { Request } from "@/shared/api/http/http-request";
import { ICategoryApi } from "./types/category-api-interfaces";
import { CategoryRequestDTO, CategoryResponseDTO } from "./types/interfaces";
import { ApiEndpoints, HttpMethods } from "@/shared/api/http/enums";

class CategoryApi implements ICategoryApi {
  async getCategory(): Promise<CategoryResponseDTO> {
    return Request({
      url: ApiEndpoints.CATEGORY,
      method: HttpMethods.GET
    })
  }

  async createCategory(data: CategoryRequestDTO):Promise<CategoryResponseDTO> {
    return Request({
      url: ApiEndpoints.CATEGORY,
      method: HttpMethods.POST,
      body: data
    })
  }
}

export {CategoryApi}