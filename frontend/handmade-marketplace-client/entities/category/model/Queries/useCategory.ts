import { useQuery } from "@tanstack/react-query";
import {categoryService} from '../index'

function useCategoryQuery() {
  const {data: allCategories, isPending} = useQuery({
    queryKey: ['category'],
    queryFn: () => categoryService.getCategory(),
    refetchOnWindowFocus: false
  })

  return {allCategories, isPending};
}

export default useCategoryQuery;