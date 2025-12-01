import { Request } from "@/shared/api/http/http-request";
import { ApiEndpoints, HttpMethods } from "@/shared/api/http/enums";
import { ICategoryApi } from "../types";
import { CategoryRequestDTO, CategoryResponseDTO } from "../types/interfaces";

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